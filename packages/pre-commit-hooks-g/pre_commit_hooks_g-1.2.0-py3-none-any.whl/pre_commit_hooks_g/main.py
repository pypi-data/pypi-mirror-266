"""Python wrapper for pre-commit hook for G Code."""
import argparse
import subprocess
from pathlib import Path
from typing import Sequence


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse arguments coming from the main function.

    Args:
        argv (Sequence[str] | None, optional): arguments if existent.

    Returns:
        argparse.Namespace: object with parsed arguments
    """
    parser = argparse.ArgumentParser(description="Pre-commit hook for G code")
    parser.add_argument(
        "--hook-args", help="Arguments to the hook", dest="hook_args", nargs="*"
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to check.")
    parser.add_argument("-v", "--vi", help="Hook VI Name.", required=True, dest="vi")
    parser.add_argument(
        "--debug",
        help="Debug mode for the hook wrapper",
        dest="debug",
        action="store_true",
    )
    parser.add_argument(
        "--allow-dialogs",
        help="Allow dialogs option for G-Cli",
        dest="dialogs",
        action="store_true",
    )
    args = parser.parse_args(argv)
    return args


class VIFileNames:
    """Process paths and get VI Filenames for the wrapper and the hook."""

    def __init__(self):
        """Initialize class and assign attributes."""
        self.this_file_directory = Path(__file__).parent

    def wrapper_vi_path(self) -> Path:
        """Build path for the commit hook wrapper vi.

        Returns:
            str: returns a string (path-like) for the wrapper
        """
        return Path(self.this_file_directory / "hooks-wrapper" / "hooks-wrapper.vi")

    def hook_vi_path(self, hook_vi: str) -> Path:
        """Build path for the commit hook vi.

        Args:
            hook_vi (str): vi name of the hook.

        Returns:
            str: returns a string (path-like) for the wrapper
        """
        return Path(self.this_file_directory / "g-hooks" / hook_vi)


def build_gcli_cmd_line(
    wrapper_vi: str,
    hook_vi: str,
    filenames: list,
    debug: bool = False,
    allow_dialogs: bool = False,
    extra_args: Sequence[str] | None = None,
) -> Sequence[str]:
    """Build command line for G-CLI according to arguments.

    Args:
        wrapper_vi (str): wrapper vi for hooks.
        hook_vi (str): target hook vi to be called by the wrapper.
        filenames (str): filename to be evaluated by the hook.
        debug (bool): if debugging flag in hook-wrapper VI.
        allow_dialogs (bool, optional): g-cli allow-dialogs flag. Defaults to False.
        extra_args (Sequence[str], optional): extra args to the hook. Defaults to [].

    Returns:
        Sequence[str]: created command line used by subprocess call
    """
    cmd_line = ["g-cli"]

    if allow_dialogs:
        cmd_line.append("--allow-dialogs")
    cmd_line.extend([wrapper_vi, "--"])
    if debug:
        cmd_line.append("-debug")
    cmd_line.extend(["-hook-path", hook_vi, "-files"])
    cmd_line.append(",".join([str(filename) for filename in filenames]))
    if extra_args:
        cmd_line.extend(extra_args)  # type: ignore

    return cmd_line


def main(argv: Sequence[str] | None = None) -> int:
    """Main function that calls the G hook and get return code.

    Args:
        argv (Sequence[str] | None, optional): arguments if existent

    Returns:
        int:  return code from hook
    """
    args = parse_arguments(argv)

    filepaths = VIFileNames()
    hook_wrapper_vi = filepaths.wrapper_vi_path()
    hook_vi = filepaths.hook_vi_path(hook_vi=args.vi)

    retval = 0
    filenames = args.filenames
    cmd_line = build_gcli_cmd_line(
        wrapper_vi=str(hook_wrapper_vi),
        hook_vi=str(hook_vi),
        filenames=filenames,
        allow_dialogs=args.dialogs,
        debug=args.debug,
        extra_args=args.hook_args,
    )
    process = subprocess.run(
        cmd_line,
        shell=True,
        check=False,
    )
    retval |= process.returncode

    return retval


if __name__ == "__main__":
    raise SystemExit(main())
