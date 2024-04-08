import sys
import glob
import os
import argparse
import sys
from .commands import test, add_test_arguments


class CustomFormatter(argparse.RawTextHelpFormatter):
    """Custom formatter for argparse to include aliases in help messages."""

    def _format_action(self, action):
        parts = super()._format_action(action)
        if hasattr(action, "aliases"):  # Check if 'aliases' attribute exists
            parts = "\n".join([parts, f"Aliases: {', '.join(action.aliases)}"])
        return parts


def ggun():
    """Main function for the CLI tool."""
    parser = argparse.ArgumentParser(
        prog="ggun",
        description="Ggun CLI tool for smart contract management" " and development.",
        formatter_class=CustomFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version="%(prog)s 1.0")
    subparsers = parser.add_subparsers(
        dest="command", help="Commands", metavar="COMMAND"
    )
    # Commands
    subparsers.add_parser("bind", help="Generate Rust bindings for smart contracts")
    subparsers.add_parser(
        "build", help="Build the project's smart contracts [Aliases: b, compile]"
    ).aliases = ["b", "compile"]
    subparsers.add_parser("cache", help="Manage the Foundry cache")
    subparsers.add_parser(
        "clean", help="Remove the build artifacts and cache directories [Aliases: cl]"
    ).aliases = ["cl"]
    subparsers.add_parser(
        "completions", help="Generate shell completions script [Aliases: com]"
    ).aliases = ["com"]
    subparsers.add_parser(
        "config", help="Display the current config [Aliases: co]"
    ).aliases = ["co"]
    subparsers.add_parser("coverage", help="Generate coverage reports")
    subparsers.add_parser(
        "create", help="Deploy a smart contract [Aliases: c]"
    ).aliases = ["c"]
    subparsers.add_parser(
        "debug", help="Debugs a single smart contract as a script [Aliases: d]"
    ).aliases = ["d"]
    subparsers.add_parser("doc", help="Generate documentation for the project")
    subparsers.add_parser(
        "flatten",
        help="Flatten a source file and all of its imports into one file [Aliases: f]",
    ).aliases = ["f"]
    subparsers.add_parser("fmt", help="Format Solidity source files")
    subparsers.add_parser(
        "geiger",
        help="Detects usage of unsafe cheat codes in a project and its dependencies",
    )
    subparsers.add_parser("generate", help="Generate scaffold files")
    subparsers.add_parser(
        "generate-fig-spec", help="Generate Fig autocompletion spec [Aliases: fig]"
    ).aliases = ["fig"]
    subparsers.add_parser(
        "help", help="Print this message or the help of the given subcommand(s)"
    )
    subparsers.add_parser("init", help="Create a new Forge project")
    subparsers.add_parser(
        "inspect",
        help="Get specialized information about a smart contract [Aliases: in]",
    ).aliases = ["in"]
    subparsers.add_parser(
        "install", help="Install one or multiple dependencies [Aliases: i]"
    ).aliases = ["i"]
    subparsers.add_parser(
        "remappings",
        help="Get the automatically inferred remappings for the project [Aliases: re]",
    ).aliases = ["re"]
    subparsers.add_parser(
        "remove", help="Remove one or multiple dependencies [Aliases: rm]"
    ).aliases = ["rm"]
    subparsers.add_parser(
        "script",
        help="Run a smart contract as a script, building transactions that can be sent onchain",
    )
    subparsers.add_parser(
        "selectors", help="Function selector utilities [Aliases: se]"
    ).aliases = ["se"]
    subparsers.add_parser(
        "snapshot", help="Create a snapshot of each test's gas usage [Aliases: s]"
    ).aliases = ["s"]

    #########################################
    # Test command
    #########################################
    test_parser = subparsers.add_parser(
        "test",
        help="Run the project's tests [Aliases: t]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    test_parser.aliases = ["t"]
    add_test_arguments(test_parser)

    subparsers.add_parser(
        "tree",
        help="Display a tree visualization of the project's dependency graph [Aliases: tr]",
    ).aliases = ["tr"]
    subparsers.add_parser(
        "update", help="Update one or multiple dependencies [Aliases: u]"
    ).aliases = ["u"]
    subparsers.add_parser(
        "verify-check", help="Check verification status on Etherscan [Aliases: vc]"
    ).aliases = ["vc"]
    subparsers.add_parser(
        "verify-contract", help="Verify smart contracts on Etherscan [Aliases: v]"
    ).aliases = ["v"]

    # Change the part where commands are executed to capture additional arguments
    args, unknown_args = parser.parse_known_args()

    if args.command == "test":
        current_directory = os.getcwd()
        test(current_directory, *unknown_args)
        return

    # The check below is now redundant, as argparse will enforce a command
    # But you can still use it for custom error handling if needed
    if args.command is None:
        parser.print_help(sys.stderr)
        info_msg = (
            "\nFind more information in the book:"
            "\nhttp://book.getfoundry.sh/reference/forge/forge.html"
        )
        print(info_msg)
        sys.exit(1)

    print(f"Executing command: {args.command}")

    # Most commands are currently unimplemented, if we get to this part it is definitely unimplemented
    print(f"Command not implemented yet: ggun {args.command}")


if __name__ == "__main__":
    ggun()
