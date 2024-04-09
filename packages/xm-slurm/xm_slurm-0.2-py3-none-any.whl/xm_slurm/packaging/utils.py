import collections
import concurrent.futures
import functools
import hashlib
import logging
import os
import pathlib
import pty
import re
import select
import shutil
import subprocess
import typing
from typing import Callable, Concatenate, Hashable, Literal, ParamSpec, Sequence, TypeVar

from xmanager import xm

from xm_slurm.packaging.registry import IndexedContainer

T = TypeVar("T")
P = ParamSpec("P")
ReturnT = TypeVar("ReturnT")


def hash_digest(obj: Hashable) -> str:
    # obj_hash = hash(obj)
    # unsigned_obj_hash = obj_hash.from_bytes(
    #     obj_hash.to_bytes((obj_hash.bit_length() + 7) // 8, "big", signed=True),
    #     "big",
    #     signed=False,
    # )
    # return hex(unsigned_obj_hash).removeprefix("0x")
    return hashlib.sha256(repr(obj).encode()).hexdigest()


def collect_executors_by_executable(
    targets: Sequence[IndexedContainer[xm.Packageable]],
) -> dict[xm.ExecutableSpec, set[xm.ExecutorSpec]]:
    executors_by_executable = collections.defaultdict(set)
    for target in targets:
        executors_by_executable[target.value.executable_spec].add(target.value.executor_spec)
    return executors_by_executable


def parallel_map(
    f: Callable[Concatenate[T, P], ReturnT],
) -> Callable[Concatenate[Sequence[T], P], list[ReturnT]]:
    @functools.wraps(f)
    def decorator(sequence: Sequence[T], *args: P.args, **kwargs: P.kwargs) -> list[ReturnT]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return list(executor.map(lambda x: f(x, *args, **kwargs), sequence))

    return decorator


# Cursor commands to filter out from the command data stream
cursor_commands_regex = re.compile(
    rb"\x1b\[\?25[hl]"  # Matches cursor show/hide commands (CSI ?25h and CSI ?25l)
    rb"|\x1b\[[0-9;]*[Hf]"  # Matches cursor position commands (CSI n;mH and CSI n;mf)
    rb"|\x1b\[s"  # Matches cursor save position (CSI s)
    rb"|\x1b\[u"  # Matches cursor restore position (CSI u)
    rb"|\x1b\[2J"  # Matches clear screen (CSI 2J)
    rb"|\x1b\[K"  # Matches clear line (CSI K)
)


@typing.overload
def run_command(
    args: Sequence[str] | xm.SequentialArgs,
    env: dict[str, str] | None = ...,
    tty: bool = ...,
    cwd: str | os.PathLike[str] | None = ...,
    check: bool = ...,
    return_stdout: Literal[False] = False,
    return_stderr: Literal[False] = False,
) -> subprocess.CompletedProcess[None]: ...


@typing.overload
def run_command(
    args: Sequence[str] | xm.SequentialArgs,
    env: dict[str, str] | None = ...,
    tty: bool = ...,
    cwd: str | os.PathLike[str] | None = ...,
    check: bool = ...,
    return_stdout: Literal[True] = True,
    return_stderr: Literal[False] = False,
) -> subprocess.CompletedProcess[str]: ...


@typing.overload
def run_command(
    args: Sequence[str] | xm.SequentialArgs,
    env: dict[str, str] | None = ...,
    tty: bool = ...,
    cwd: str | os.PathLike[str] | None = ...,
    check: bool = ...,
    return_stdout: Literal[False] = False,
    return_stderr: Literal[True] = True,
) -> subprocess.CompletedProcess[str]: ...


@typing.overload
def run_command(
    args: Sequence[str] | xm.SequentialArgs,
    env: dict[str, str] | None = ...,
    tty: bool = ...,
    cwd: str | os.PathLike[str] | None = ...,
    check: bool = ...,
    return_stdout: Literal[True] = True,
    return_stderr: Literal[True] = True,
) -> subprocess.CompletedProcess[str]: ...


def run_command(
    args: Sequence[str] | xm.SequentialArgs,
    env: dict[str, str] | None = None,
    tty: bool = False,
    cwd: str | os.PathLike[str] | None = None,
    check: bool = False,
    return_stdout: bool = False,
    return_stderr: bool = False,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[None]:
    if isinstance(args, xm.SequentialArgs):
        args = args.to_list()
    args = list(args)

    executable = shutil.which(args[0])
    if not executable:
        raise RuntimeError(f"Couldn't find executable {args[0]}")
    executable = pathlib.Path(executable)

    subprocess_env = os.environ.copy() | (env if env else {})
    if executable.name == "docker" and args[1] == "buildx":
        subprocess_env |= {"DOCKER_CLI_EXPERIMENTAL": "enabled"}

    logging.debug(f"env: {subprocess_env}")
    logging.debug(f"command: {' '.join(args)}")

    stdout_master, stdout_slave = pty.openpty()
    stderr_master, stderr_slave = pty.openpty()

    stdout_data, stderr_data = b"", b""
    with subprocess.Popen(
        executable=executable,
        args=args,
        shell=False,
        text=True,
        bufsize=0,
        stdout=stdout_slave,
        stderr=stderr_slave,
        start_new_session=True,
        close_fds=True,
        cwd=cwd,
        env=subprocess_env,
    ) as process:
        os.close(stdout_slave)
        os.close(stderr_slave)

        fds = [stdout_master, stderr_master]
        while fds:
            rlist, _, _ = select.select(fds, [], [])
            for fd in rlist:
                try:
                    data = os.read(fd, 1024)
                except OSError:
                    data = None

                if not data:
                    os.close(fd)
                    fds.remove(fd)
                    continue

                data = re.sub(cursor_commands_regex, b"", data)

                if fd == stdout_master:
                    if return_stdout:
                        stdout_data += data
                    if tty:
                        os.write(pty.STDOUT_FILENO, data)
                elif fd == stderr_master:
                    if return_stderr:
                        stderr_data += data
                    if tty:
                        os.write(pty.STDERR_FILENO, data)
                else:
                    raise RuntimeError("Unexpected file descriptor")

    stdout = stdout_data.decode(errors="replace") if stdout_data else None
    stderr = stderr_data.decode(errors="replace") if stderr_data else None

    retcode = process.poll()
    assert retcode is not None

    if check and retcode:
        raise subprocess.CalledProcessError(retcode, process.args)
    return subprocess.CompletedProcess(
        process.args,
        retcode,
        stdout=stdout,
        stderr=stderr,
    )
