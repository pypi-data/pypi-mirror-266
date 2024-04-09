import argparse
import asyncio
import contextlib
import functools
import io
import logging
import pathlib
import shlex
import stat
import string
import sys
import tempfile
import termios
import time
import tty
import typing

import paramiko
import paramiko.sftp_client
import rich.console
import rich.logging
import rich.markup
import rich.progress
import version
import watchdog.events
import watchdog.observers

REMOTE_USERNAME = 'devstack-user'
REMOTE_SOURCE_DIRECTORY = '/home/devstack-user/starflows'
REMOTE_OUTPUT_DIRECTORY = '/home/devstack-user/starflows-output'
EVENT_DEBOUNCE_SECONDS = .5

logging.basicConfig(level=logging.INFO, handlers=[rich.logging.RichHandler()], format='%(message)s')
logger = logging.getLogger('cli')

class SubprocessError(Exception):
    """A subprocess call returned with non-zero."""


class FileSystemEventHandlerToQueue(watchdog.events.FileSystemEventHandler):
    def __init__(
            self: 'FileSystemEventHandlerToQueue',
            queue: asyncio.Queue,
            loop: asyncio.BaseEventLoop,
            *args,
            **kwargs,
    ) -> None:
        self._loop = loop
        self._queue = queue
        super(*args, **kwargs)

    def on_any_event(
            self: 'FileSystemEventHandlerToQueue',
            event: watchdog.events.FileSystemEvent,
    ) -> None:
        if event.event_type in (
                watchdog.events.EVENT_TYPE_OPENED,
                watchdog.events.EVENT_TYPE_CLOSED,
        ):
            return
        if event.event_type == watchdog.events.EVENT_TYPE_MODIFIED and event.is_directory:
            return
        if '/.git' in event.src_path:
            return
        if hasattr(event, 'dest_path') and '/.git' in event.dest_path:
            return
        self._loop.call_soon_threadsafe(self._queue.put_nowait, event)


async def run_subprocess(
        program: str,
        args: str,
        *,
        name: str,
        cwd: typing.Optional[pathlib.Path] = None,
        env: typing.Optional[dict] = None,
        capture_stdout: bool = True,
        print_stdout: bool = True,
        capture_stderr: bool = True,
        print_stderr: bool = True,
) -> None:
    args_str = ' '.join(args)
    process = await asyncio.create_subprocess_exec(
        program,
        *args,
        cwd=cwd,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE if capture_stdout else asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE if capture_stderr else asyncio.subprocess.DEVNULL,
        env=env,
    )
    stdout = b''
    stderr = b''
    try:
        if not capture_stdout and not capture_stderr:
            await process.wait()
        else:
            tasks = set()
            if capture_stdout:
                stdout_readline = asyncio.create_task(process.stdout.readline())
                tasks.add(stdout_readline)
            if capture_stderr:
                stderr_readline = asyncio.create_task(process.stderr.readline())
                tasks.add(stderr_readline)
            while process.returncode is None:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if capture_stdout and stdout_readline in done:
                    stdout_line = await stdout_readline
                    if print_stdout and stdout_line.decode().strip():
                        logger.info('%s: %s', name, stdout_line.decode().strip())
                    stdout += stdout_line + b'\n'
                    stdout_readline = asyncio.create_task(process.stdout.readline())
                    pending.add(stdout_readline)
                if capture_stderr and stderr_readline in done:
                    stderr_line = await stderr_readline
                    if print_stderr and stderr_line.decode().strip():
                        logger.warning('%s: %s', name, stderr_line.decode().strip())
                    stderr += stderr_line + b'\n'
                    stderr_readline = asyncio.create_task(process.stderr.readline())
                    pending.add(stderr_readline)
                tasks = pending
    finally:
        if process.returncode is None:
            logger.debug('Terminating "%s %s"', program, args_str)
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=3)
            except asyncio.TimeoutError:
                logger.info('Killing "%s %s"', program, args_str)
                process.kill()
                await asyncio.wait_for(process.wait(), timeout=3)
    if process.returncode:
        if cwd is None:
            msg = f'Command "{program} {args_str}" failed with returncode {process.returncode}.'
        else:
            msg = f'Command "{program} {args_str}" in "{cwd}" failed with returncode {process.returncode}.'
        raise SubprocessError(msg)
    logger.debug(
        'Command "%s %s" succeeded.',
        program,
        args_str,
    )
    return stdout, stderr


def _get_event_significant_path(event: watchdog.events.FileSystemEvent) -> str:
    if hasattr(event, 'dest_path'):
        return event.dest_path
    return event.src_path


def is_relative_to(self: pathlib.Path, other: pathlib.Path) -> bool:
    return other == self or other in self.parents


class Cli:
    def __init__(self: 'Cli', args: argparse.Namespace) -> None:
        rich.print(f'Cloudomation devstack-cli {version.MAJOR}+{version.BRANCH_NAME}.{version.BUILD_DATE}.{version.SHORT_SHA}')
        self.hostname = args.hostname
        self.local_source_directory = pathlib.Path(args.source_directory)

        self.local_output_directory = pathlib.Path(args.output_directory) if args.output_directory else None
        if (
                self.local_output_directory is not None
                and (
                    is_relative_to(self.local_source_directory, self.local_output_directory)
                    or is_relative_to(self.local_output_directory, self.local_source_directory)
                )
        ):
            logger.error('Source-directory and output-directory must not overlap!')
            sys.exit(1)
        self.ssh_client = None
        self.sftp_client = None
        self.filesystem_watch_task = None
        self.known_hosts_file = None
        self.console = rich.console.Console()
        if args.verbose:
            logger.setLevel(logging.DEBUG)

    async def run(self: 'Cli') -> None:
        self.loop = asyncio.get_running_loop()
        key_queue = asyncio.Queue()
        await self._prepare_known_hosts()
        try:
            await self._connect_to_rde()
            await self._init_local_cache()
            sync_task = asyncio.create_task(self._start_sync())
            port_forwarding_task = asyncio.create_task(self._start_port_forwarding())
            logs_task = None
            await self._setup_keyboard(key_queue)
            try:
                logger.info('Ready!')
                key_queue.put_nowait('h')
                while True:
                    key_press = await key_queue.get()
                    # check status
                    if sync_task is not None and sync_task.done():
                        sync_task = None
                    if port_forwarding_task is not None and port_forwarding_task.done():
                        port_forwarding_task = None
                    if logs_task is not None and logs_task.done():
                        logs_task = None

                    if key_press == 'h':
                        table = rich.table.Table(title='Help')
                        table.add_column('Key', style='cyan')
                        table.add_column('Function')
                        table.add_column('Status')
                        table.add_row('h', 'Print help')
                        table.add_row('v', 'Toggle debug logs', '[green]on' if logger.getEffectiveLevel() == logging.DEBUG else '[red]off')
                        table.add_row('s', 'Toggle file sync', '[red]off' if sync_task is None else '[green]on')
                        table.add_row('p', 'Toggle port forwarding', '[red]off' if port_forwarding_task is None else '[green]on')
                        table.add_row('l', 'Toggle following logs', '[red]off' if logs_task is None else '[green]on')
                        table.add_row('q', 'Quit')
                        rich.print(table)
                    elif key_press == 'v':
                        if logger.getEffectiveLevel() == logging.INFO:
                            logger.info('Enabling debug logs')
                            logger.setLevel(logging.DEBUG)
                        else:
                            logger.info('Disabling debug logs')
                            logger.setLevel(logging.INFO)
                    elif key_press == 's':
                        if sync_task is None:
                            sync_task = asyncio.create_task(self._start_sync())
                        else:
                            sync_task.cancel()
                            try:
                                await sync_task
                            except asyncio.CancelledError:
                                pass
                            except Exception:
                                logger.exception('Error during file sync')
                            sync_task = None
                    elif key_press == 'p':
                        if port_forwarding_task is None:
                            port_forwarding_task = asyncio.create_task(self._start_port_forwarding())
                        else:
                            port_forwarding_task.cancel()
                            try:
                                await port_forwarding_task
                            except asyncio.CancelledError:
                                pass
                            except Exception:
                                logger.exception('Error during port forwarding')
                            port_forwarding_task = None
                    elif key_press == 'l':
                        if logs_task is None:
                            logs_task = asyncio.create_task(self._start_logs())
                        else:
                            logs_task.cancel()
                            try:
                                await logs_task
                            except asyncio.CancelledError:
                                pass
                            except Exception:
                                logger.exception('Error during logs')
                            logs_task = None
                    elif key_press == 'q':
                        break
                    elif ord(key_press) == 10:  # return
                        rich.print('')
                    else:
                        logger.debug('Unknown keypress "%s" (%d)', key_press if key_press in string.printable else '?', ord(key_press))
            finally:
                await self._reset_keyboard()
                if port_forwarding_task is not None:
                    port_forwarding_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await port_forwarding_task
                if sync_task is not None:
                    sync_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await sync_task
                if logs_task is not None:
                    logs_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await logs_task
            await self._disconnect_from_rde()
        finally:
            await self._cleanup_known_hosts_file()

    async def _setup_keyboard(self: 'Cli', queue: asyncio.Queue) -> None:
        self._fd = sys.stdin.fileno()
        self._tcattr = termios.tcgetattr(self._fd)
        tty.setcbreak(self._fd)
        def on_stdin() -> None:
            self.loop.call_soon_threadsafe(queue.put_nowait, sys.stdin.read(1))
        self.loop.add_reader(sys.stdin, on_stdin)

    async def _reset_keyboard(self: 'Cli') -> None:
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._tcattr)
        self.loop.remove_reader(sys.stdin)

    async def _prepare_known_hosts(self: 'Cli') -> None:
        self.known_hosts_file = tempfile.NamedTemporaryFile(delete=False)
        logger.info('Writing temporary known_hosts file "%s"', self.known_hosts_file.name)
        logger.debug('Scanning hostkeys of "%s"', self.hostname)
        try:
            stdout, stderr = await run_subprocess(
                'ssh-keyscan',
                [
                    self.hostname,
                ],
                name='ssh-keyscan',
                print_stdout=False,
                print_stderr=False,
            )
        except SubprocessError as ex:
            logger.error('%s Failed to fetch hostkeys. Is you RDE running?', ex)  # noqa: TRY400
            sys.exit(1)
        self.known_hosts_file.write(stdout)
        with contextlib.suppress(FileNotFoundError):
            self.known_hosts_file.write(pathlib.Path('~/.ssh/known_hosts').expanduser().read_bytes())
        self.known_hosts_file.close()

    async def _cleanup_known_hosts_file(self: 'Cli') -> None:
        if self.known_hosts_file is None:
            return
        pathlib.Path(self.known_hosts_file.name).unlink()

    async def _connect_to_rde(self: 'Cli') -> None:
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logger.info('Connecting to RDE')
        try:
            self.ssh_client.connect(
                hostname=self.hostname,
                username=REMOTE_USERNAME,
                timeout=30,
            )
        except TimeoutError:
            logger.exception('Timeout while connecting to RDE. Is your RDE running?')
            sys.exit(1)
            return
        transport = self.ssh_client.get_transport()
        self.sftp_client = paramiko.sftp_client.SFTPClient.from_transport(transport)

    async def _disconnect_from_rde(self: 'Cli') -> None:
        if self.sftp_client is not None:
            self.sftp_client.close()
            self.sftp_client = None
        if self.ssh_client is not None:
            self.ssh_client.close()
            self.ssh_client = None

    async def _init_local_cache(self: 'Cli') -> None:
        self.local_source_directory.mkdir(parents=True, exist_ok=True)
        logger.debug('Listing remote items')
        listing = self.sftp_client.listdir_attr(REMOTE_SOURCE_DIRECTORY)

        logger.info('Processing %d remote items...', len(listing))
        for file_info in rich.progress.track(
                sequence=sorted(
                    listing,
                    key=lambda file_info: file_info.filename.casefold(),
                ),
                description='Processing remote items',
        ):
            logger.info('Processing "%s"', file_info.filename)
            try:
                result = await self._process_remote_item(file_info)
            except SubprocessError:
                logger.exception('Failed')
            else:
                logger.info(result)

    async def _process_remote_item(self: 'Cli', file_info: paramiko.sftp_attr.SFTPAttributes) -> str:
        filename = file_info.filename

        if file_info.st_mode & stat.S_IFDIR:
            # check if .git exists
            try:
                git_stat = self.sftp_client.stat(f'{REMOTE_SOURCE_DIRECTORY}/{filename}/.git')
            except FileNotFoundError:
                pass
            else:
                if git_stat.st_mode & stat.S_IFDIR:
                    repo_dir = self.local_source_directory / filename
                    if not repo_dir.exists():
                        return await self._process_remote_item_clone(file_info.filename)
                    return f'Repository "{filename}" already exists'
            return await self._process_remote_item_copy_dir(file_info.filename)
        return await self._process_remote_item_copy_file(file_info.filename)

    async def _process_remote_item_copy_dir(self: 'Cli', filename: str) -> str:
        await run_subprocess(
            'rsync',
            [
                '-e', f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
                '--archive',
                '--checksum',
                f'{REMOTE_USERNAME}@{self.hostname}:{REMOTE_SOURCE_DIRECTORY}/{filename}/',
                str(self.local_source_directory / filename),
            ],
            name='Copy remote directory',
        )
        return f'Copied directory "{filename}"'

    async def _process_remote_item_copy_file(self: 'Cli', filename: str) -> str:
        await self.loop.run_in_executor(
            executor=None,
            func=functools.partial(
                self.sftp_client.get,
                remotepath=f'{REMOTE_SOURCE_DIRECTORY}/{filename}',
                localpath=str(self.local_source_directory / filename),
            ),
        )
        return f'Copied file "{filename}"'

    async def _process_remote_item_clone(self: 'Cli', filename: str) -> str:
        await run_subprocess(
            'git',
            [
                'clone',
                '-q',
                f'{REMOTE_USERNAME}@{self.hostname}:{REMOTE_SOURCE_DIRECTORY}/{filename}',
            ],
            name='Git clone',
            cwd=self.local_source_directory,
            env={
                'GIT_SSH_COMMAND': f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
            },
        )
        ssh_stdin, ssh_stdout, ssh_stderr = await self.loop.run_in_executor(
            executor=None,
            func=functools.partial(
                self.ssh_client.exec_command,
                shlex.join([
                    'git',
                    '-C',
                    f'{REMOTE_SOURCE_DIRECTORY}/{filename}',
                    'config',
                    '--get',
                    'remote.origin.url',
                ]),
            ),
        )
        upstream = ssh_stdout.readline().strip()
        await run_subprocess(
            'git',
            [
                'remote',
                'set-url',
                'origin',
                upstream,
            ],
            name='Git remote set-url',
            cwd=self.local_source_directory / filename,
            env={
                'GIT_SSH_COMMAND': f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
            },
        )
        return f'Cloned repository "{filename}"'

    async def _start_sync(self: 'Cli') -> None:
        logger.info('Starting file sync')
        filesystem_event_queue = asyncio.Queue()
        filesystem_watch_task = asyncio.create_task(
            self._watch_filesystem(
                queue=filesystem_event_queue,
            ),
        )
        if self.local_output_directory:
            remote_sync_task = asyncio.create_task(
                self._remote_sync(),
            )
        else:
            remote_sync_task = None
        background_sync_task = None
        try:
            while True:
                filesystem_events = []
                if background_sync_task is not None:
                    background_sync_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await background_sync_task
                background_sync_task = asyncio.create_task(self._background_sync())
                filesystem_events.append(await filesystem_event_queue.get())
                logger.debug('first event, debouncing...')
                # debounce
                await asyncio.sleep(EVENT_DEBOUNCE_SECONDS)
                logger.debug('collecting changes')
                while not filesystem_event_queue.empty():
                    filesystem_events.append(filesystem_event_queue.get_nowait())
                for event in filesystem_events:
                    logger.debug('non-unique event: %s', event)
                # remove duplicates
                events = [
                    event
                    for i, event
                    in enumerate(filesystem_events)
                    if _get_event_significant_path(event) not in (
                        _get_event_significant_path(later_event)
                        for later_event
                        in filesystem_events[i+1:]
                    )
                ]
                for i, event in enumerate(events, start=1):
                    logger.debug('unique event [%d/%d]: %s', i, len(events), event)
                    await self._process_sync_event(event)
        except asyncio.CancelledError:
            logger.info('File sync interrupted')
            raise
        except Exception:
            logger.exception('File sync failed')
        else:
            logger.info('File sync stopped')
        finally:
            filesystem_watch_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await filesystem_watch_task
            if remote_sync_task is not None:
                remote_sync_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await remote_sync_task
            if background_sync_task is not None:
                background_sync_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await background_sync_task

    async def _background_sync(self: 'Cli') -> None:
        logger.debug('Starting background sync')
        self.local_source_directory.mkdir(parents=True, exist_ok=True)
        with contextlib.suppress(OSError):
            self.sftp_client.mkdir(REMOTE_SOURCE_DIRECTORY)
        try:
            await run_subprocess(
                'rsync',
                [
                    '-e', f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
                    '--archive',
                    '--delete',
                    '--exclude', 'build-cache-*',  # TODO: make exclusions configurable
                    '--exclude', 'dev-tool/config',
                    '--exclude', 'alembic.ini',
                    '--exclude', 'cypress/screenshots',
                    '--exclude', 'cypress/videos',
                    '--exclude', 'flow_api',
                    '--exclude', '.git',
                    '--exclude', '__pycache__',
                    '--exclude', '.cache',
                    '--exclude', 'node_modules',
                    '--exclude', '.venv',
                    '--exclude', 'bundle-content',  # until https://app.clickup.com/t/86bxn0exx
                    '--exclude', 'cloudomation-fe/build',
                    '--exclude', 'devstack-self-service-portal/vite-cache',
                    '--exclude', 'devstack-self-service-portal/dist',
                    '--exclude', 'documentation/generator/generated',
                    '--exclude', 'version.py',
                    '--exclude', 'instantclient-basic-linux.x64.zip',
                    '--exclude', 'msodbcsql.deb',
                    '--exclude', 'auth/report',
                    '--exclude', 'cloudomation-fe/.env',
                    '--exclude', 'cloudomation/tmp_git_task',
                    '--exclude', 'cloudomation/tmp',
                    '--exclude', 'cloudomation/notifications',
                    '--exclude', 'documentation/versioned_docs',
                    '--human-readable',
                    '--info=name1',
                    f'{self.local_source_directory}/',
                    f'{REMOTE_USERNAME}@{self.hostname}:{REMOTE_SOURCE_DIRECTORY}',
                ],
                name='Background sync',
            )
        except asyncio.CancelledError:
            logger.debug('Background sync interrupted')
            raise
        except SubprocessError as ex:
            logger.error('Background sync failed: %s', ex)  # noqa: TRY400
        except Exception:
            logger.exception('Background sync failed')
        else:
            logger.info('Background sync done')

    async def _reverse_background_sync(self: 'Cli') -> None:
        logger.debug('Starting reverse background sync')
        with contextlib.suppress(OSError):
            self.sftp_client.mkdir(REMOTE_OUTPUT_DIRECTORY)
        self.local_output_directory.mkdir(parents=True, exist_ok=True)
        try:
            stdout, stderr = await run_subprocess(
                'rsync',
                [
                    '-e', f'ssh -o ConnectTimeout=10 -o UserKnownHostsFile={self.known_hosts_file.name}',
                    '--archive',
                    '--exclude', '__pycache__',
                    '--human-readable',
                    '--info=name1',
                    f'{REMOTE_USERNAME}@{self.hostname}:{REMOTE_OUTPUT_DIRECTORY}/',
                    str(self.local_output_directory),
                ],
                name='Reverse background sync',
            )
        except asyncio.CancelledError:
            logger.debug('Reverse background sync interrupted')
            raise
        except SubprocessError:
            logger.exception('Reverse background sync failed')
        else:
            logger.debug('Reverse background sync done')

    async def _watch_filesystem(
            self: 'Cli',
            queue: asyncio.Queue,
    ) -> None:
        handler = FileSystemEventHandlerToQueue(queue, self.loop)
        filesystem_observer = watchdog.observers.Observer()
        filesystem_observer.schedule(
            event_handler=handler,
            path=str(self.local_source_directory),
            recursive=True,
        )
        filesystem_observer.start()
        logger.info('Filesystem watches established')
        try:
            await self.loop.run_in_executor(
                executor=None,
                func=filesystem_observer.join,
            )
        finally:
            filesystem_observer.stop()
            filesystem_observer.join(3)

    async def _remote_sync(self: 'Cli') -> None:
        while True:
            await self._reverse_background_sync()
            await asyncio.sleep(10)

    async def _process_sync_event(self: 'Cli', event: watchdog.events.FileSystemEvent) -> None:
        local_path = pathlib.Path(event.src_path)
        relative_path = local_path.relative_to(self.local_source_directory)
        remote_path = f'{REMOTE_SOURCE_DIRECTORY}/{relative_path}'
        if isinstance(event, watchdog.events.DirCreatedEvent):
            await self._remote_directory_create(remote_path)
        elif isinstance(event, watchdog.events.DirDeletedEvent):
            await self._remote_directory_delete(remote_path)
        elif isinstance(event, watchdog.events.FileCreatedEvent):
            await self._remote_file_create(remote_path)
        elif isinstance(event, watchdog.events.FileModifiedEvent):
            stat = local_path.stat()
            times = (stat.st_atime, stat.st_mtime)
            await self._remote_file_copy(event.src_path, remote_path, times)
        elif isinstance(event, watchdog.events.FileDeletedEvent):
            await self._remote_file_delete(remote_path)
        elif isinstance(event, watchdog.events.FileMovedEvent):
            dest_local_path = pathlib.Path(event.dest_path)
            dest_relative_path = dest_local_path.relative_to(self.local_source_directory)
            dest_remote_path = f'{REMOTE_SOURCE_DIRECTORY}/{dest_relative_path}'
            stat = dest_local_path.stat()
            times = (stat.st_atime, stat.st_mtime)
            await self._remote_file_move(remote_path, dest_remote_path, times)

    async def _remote_directory_create(self: 'Cli', remote_path: str) -> None:
        logger.info('Create directory: "%s" (remote)', remote_path)
        try:
            self.sftp_client.mkdir(remote_path)
        except OSError:
            logger.exception('-> failed')
            try:
                stat = self.sftp_client.stat(remote_path)
            except FileNotFoundError:
                logger.info('-> remote directory does not exist')
            else:
                logger.info('-> remote directory already exists:\n%s', stat)

    async def _remote_directory_delete(self: 'Cli', remote_path: str) -> None:
        logger.info('Delete directory: "%s" (remote)', remote_path)
        try:
            self.sftp_client.rmdir(remote_path)
        except FileNotFoundError:
            logger.exception('-> remote directory does not exist')
        except OSError:
            logger.exception('-> failed')

    async def _remote_file_create(self: 'Cli', remote_path: str) -> None:
        logger.info('Create file: "%s" (remote)', remote_path)
        self.sftp_client.putfo(io.BytesIO(), remote_path)

    async def _remote_file_copy(self: 'Cli', local_path: str, remote_path: str, times: typing.Tuple[int, int]) -> None:
        logger.info('Copy file: "%s" (local) -> "%s" (remote)', local_path, remote_path)
        self.sftp_client.put(local_path, remote_path)
        self.sftp_client.utime(remote_path, times)

    async def _remote_file_delete(self: 'Cli', remote_path: str) -> None:
        logger.info('Delete file: "%s" (remote)', remote_path)
        try:
            self.sftp_client.remove(remote_path)
        except FileNotFoundError:
            logger.info('-> remote file does not exist')

    async def _remote_file_move(self: 'Cli', remote_path: str, dest_remote_path: str, times: typing.Tuple[int, int]) -> None:
        logger.info('Move file: "%s" (remote) -> "%s" (remote)', remote_path, dest_remote_path)
        self.sftp_client.rename(remote_path, dest_remote_path)
        self.sftp_client.utime(dest_remote_path, times)

    async def _start_port_forwarding(self: 'Cli') -> None:
        logger.info('Starting port forwarding of ports 8443, 5678, 6678, 7678, 8678, 3000, 2022')
        try:
            await run_subprocess(
                'ssh',
                [
                    '-o', 'ConnectTimeout=10',
                    '-o', f'UserKnownHostsFile={self.known_hosts_file.name}',
                    '-NT',
                    f'{REMOTE_USERNAME}@{self.hostname}',
                    '-L', '8443:localhost:443',  # TODO: make ports configurable
                    '-L', '5678:localhost:5678',
                    '-L', '6678:localhost:6678',
                    '-L', '7678:localhost:7678',
                    '-L', '8678:localhost:8678',
                    '-L', '3000:localhost:3000',
                    '-L', '2022:localhost:2022',
                ],
                name='Port forwarding',
                capture_stdout=False,
            )
        except asyncio.CancelledError:
            logger.info('Port forwarding interrupted')
            raise
        except SubprocessError:
            logger.exception('Port forwarding failed')
        else:
            logger.info('Port forwarding done')


    async def _start_logs(self: 'Cli') -> None:
        logger.info('Following logs')
        stdout_queue = asyncio.Queue()
        stderr_queue = asyncio.Queue()
        stream_task = self.loop.run_in_executor(
            executor=None,
            func=functools.partial(
                self._stream_logs,
                stdout_queue=stdout_queue,
                stderr_queue=stderr_queue,
            ),
        )
        try:
            stdout_get = asyncio.create_task(stdout_queue.get())
            stderr_get = asyncio.create_task(stderr_queue.get())
            while True:
                done, pending = await asyncio.wait(
                    {stdout_get, stderr_get},
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if stdout_get in done:
                    stdout = await stdout_get
                    if stdout is not None:
                        self.console.print(rich.markup.escape(stdout.strip()), style='default on grey23', justify='left')
                    stdout_get = asyncio.create_task(stdout_queue.get())
                if stderr_get in done:
                    stderr = await stderr_get
                    if stderr is not None:
                        self.console.print(rich.markup.escape(stderr.strip()), style='default on red', justify='left')
                    stderr_get = asyncio.create_task(stderr_queue.get())
        except asyncio.CancelledError:
            logger.info('Following logs interrupted')
            raise
        except Exception:
            logger.exception('Following logs failed')
        else:
            logger.info('Stopped following logs')
        finally:
            stream_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await stream_task


    def _stream_logs(
            self: 'Cli',
            stdout_queue: asyncio.Queue,
            stderr_queue: asyncio.Queue,
    ) -> None:
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh_client.exec_command(
            'cd /home/devstack-user/starflows/research/dev-tool && . dev.sh logs',
            get_pty=False,
            timeout=0,
        )
        ssh_stdin.close()
        have_stdout = False
        have_stderr = False
        while True:
            try:
                stdout = ssh_stdout.readline(1024)
            except TimeoutError:
                have_stdout = False
            else:
                have_stdout = True
            try:
                stderr = ssh_stderr.readline(1024)
            except TimeoutError:
                have_stderr = False
            else:
                have_stderr = True
            if have_stdout and stdout:
                self.loop.call_soon_threadsafe(stdout_queue.put_nowait, stdout)
            if have_stderr and stderr:
                self.loop.call_soon_threadsafe(stderr_queue.put_nowait, stderr)
            if have_stdout and not stdout and have_stderr and not stderr:
                break
            if not have_stdout and not have_stderr:
                time.sleep(.5)
        self.loop.call_soon_threadsafe(stdout_queue.put_nowait, None)
        self.loop.call_soon_threadsafe(stderr_queue.put_nowait, None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-H', '--hostname',
        required=True,
        help='the IP or hostname of the RDE',
    )
    parser.add_argument(
        '-s', '--source-directory',
        required=True,
        help='a local directory where the sources from the RDE are cached',
    )
    parser.add_argument(
        '-o', '--output-directory',
        help='a local directory where artifacts created on the RDE are stored',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='enable debug logging',
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'Cloudomation devstack-cli {version.MAJOR}+{version.BRANCH_NAME}.{version.BUILD_DATE}.{version.SHORT_SHA}',
    )
    args = parser.parse_args()

    cli = Cli(args)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(cli.run())
    logger.info('Bye!')


if __name__ == '__main__':
    main()
