import argparse
from utils.api_call import api_call
from utils.list_files import list_git_files, list_forge_test_strace_files
import os
from tqdm import tqdm

def test(current_directory, *args: argparse.Namespace):
    """
    Executes the test command by preparing and uploading files located in the
    current directory to the API for fuzzing.

    Args:
        current_directory (str): The directory from which files will be listed
        and prepared for upload.
        *args: Variable length argument list to capture additional arguments passed to the command.
    """
    git_tracked_files = list_forge_test_strace_files(
        current_directory,
        False,
        [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".webp",
            ".bmp",
            ".ico",
            ".jxr",
            ".psd",
            ".html",
            ".mp4",
            ".mov",
        ],
    )

    # Step 1: Prepare the files for uploading
    files_to_upload = {}
    for file_path in tqdm(git_tracked_files, desc="Preparing files"):
        if file_path and not os.path.isdir(file_path):
            files_to_upload[file_path] = open(file_path, "rb")

    if not files_to_upload:
        print("Nothing to compile")
        return

    # Upload all of the files to the API
    api_key = "YourSecretAPIKey"

    # Step 2: Run the fuzzer on the server
    fuzz_api_response = api_call(api_key, "/fuzz", "POST", files=files_to_upload)

    # Close the files after uploading
    # NOTE: This needs to be after the API call
    for file in files_to_upload.values():
        file.close()

    # Step 3: Display the fuzzing response to the user
    if fuzz_api_response:
        print("Fuzzing Test Results:")
        for key, value in fuzz_api_response.items():
            if key == "test_output":
                print(f"\nTest Output:\n{value}")
    else:
        print("Failed to get a response from the fuzzing API.")


def add_test_arguments(parser):
    # Create argument groups
    test_options_group = parser.add_argument_group("Test Options")
    display_options_group = parser.add_argument_group("Display Options")
    test_filtering_group = parser.add_argument_group("Test Filtering")
    evm_options_group = parser.add_argument_group("EVM Options")
    fork_config_group = parser.add_argument_group("Fork Config")
    executor_env_config_group = parser.add_argument_group("Executor Environment Config")
    cache_options_group = parser.add_argument_group("Cache Options")
    build_options_group = parser.add_argument_group("Build Options")
    linker_options_group = parser.add_argument_group("Linker Options")
    compiler_options_group = parser.add_argument_group("Compiler Options")
    project_options_group = parser.add_argument_group("Project Options")
    watch_options_group = parser.add_argument_group("Watch Options")

    # Test options
    test_options_group.add_argument(
        "--debug", metavar="<TEST_FUNCTION>", help="Run a test in the debugger."
    )
    test_options_group.add_argument(
        "--gas-report", action="store_true", help="Print a gas report"
    )
    test_options_group.add_argument(
        "--allow-failure",
        action="store_true",
        help="Exit with code 0 even if a test fails",
    )
    test_options_group.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop running tests after the first failure",
    )
    test_options_group.add_argument(
        "--etherscan-api-key",
        metavar="<KEY>",
        help="The Etherscan (or equivalent) API key",
    )
    test_options_group.add_argument(
        "--fuzz-seed",
        metavar="<FUZZ_SEED>",
        help="Set seed used to generate randomness during your fuzz runs",
    )
    test_options_group.add_argument(
        "--fuzz-runs", metavar="<RUNS>", help="Specify the number of fuzz runs"
    )

    # Display options
    display_options_group.add_argument(
        "-j", "--json", action="store_true", help="Output test results in JSON format"
    )
    display_options_group.add_argument(
        "-l", "--list", action="store_true", help="List tests instead of running them"
    )
    display_options_group.add_argument(
        "--summary", action="store_true", help="Print test summary table"
    )
    display_options_group.add_argument(
        "--detailed", action="store_true", help="Print detailed test summary table"
    )

    # Test filtering
    test_filtering_group.add_argument(
        "--match-test",
        metavar="<REGEX>",
        help="Only run test functions matching the specified regex pattern",
    ).aliases = ["mt"]
    test_filtering_group.add_argument(
        "--no-match-test",
        metavar="<REGEX>",
        help="Only run test functions that do not match the specified regex pattern",
    ).aliases = ["nmt"]
    test_filtering_group.add_argument(
        "--match-contract",
        metavar="<REGEX>",
        help="Only run tests in contracts matching the specified regex pattern",
    ).aliases = ["mc"]
    test_filtering_group.add_argument(
        "--no-match-contract",
        metavar="<REGEX>",
        help="Only run tests in contracts that do not match the specified regex pattern",
    ).aliases = ["nmc"]
    test_filtering_group.add_argument(
        "--match-path",
        metavar="<GLOB>",
        help="Only run tests in source files matching the specified glob pattern",
    ).aliases = ["mp"]
    test_filtering_group.add_argument(
        "--no-match-path",
        metavar="<GLOB>",
        help="Only run tests in source files that do not match the specified glob pattern",
    ).aliases = ["nmp"]

    # EVM options
    evm_options_group.add_argument(
        "-f",
        "--fork-url",
        metavar="<URL>",
        help="Fetch state over a remote endpoint instead of starting from an empty state.",
    )
    evm_options_group.add_argument(
        "--fork-block-number",
        metavar="<BLOCK>",
        help="Fetch state from a specific block number over a remote endpoint.",
    )
    evm_options_group.add_argument(
        "--fork-retries", metavar="<RETRIES>", help="Number of retries."
    )
    evm_options_group.add_argument(
        "--fork-retry-backoff",
        metavar="<BACKOFF>",
        help="Initial retry backoff on encountering errors.",
    )
    evm_options_group.add_argument(
        "--no-storage-caching",
        action="store_true",
        help="Explicitly disables the use of RPC caching.",
    )
    evm_options_group.add_argument(
        "--initial-balance",
        metavar="<BALANCE>",
        help="The initial balance of deployed test contracts",
    )
    evm_options_group.add_argument(
        "--sender",
        metavar="<ADDRESS>",
        help="The address which will be executing tests",
    )
    evm_options_group.add_argument(
        "--ffi", action="store_true", help="Enable the FFI cheatcode"
    )
    evm_options_group.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="Verbosity of the EVM. Pass multiple times to increase the verbosity.",
    )

    # Fork config
    fork_config_group.add_argument(
        "--compute-units-per-second",
        metavar="<CUPS>",
        help="Sets the number of assumed available compute units per second for this provider",
    )
    fork_config_group.add_argument(
        "--no-rpc-rate-limit",
        action="store_true",
        help="Disables rate limiting for this node's provider.",
    )

    # Executor environment config
    executor_env_config_group.add_argument(
        "--gas-limit", metavar="<GAS_LIMIT>", help="The block gas limit"
    )
    executor_env_config_group.add_argument(
        "--code-size-limit",
        metavar="<CODE_SIZE>",
        help="EIP-170: Contract code size limit in bytes.",
    )
    executor_env_config_group.add_argument(
        "--chain-id", metavar="<CHAIN_ID>", help="The chain ID"
    )
    executor_env_config_group.add_argument(
        "--gas-price", metavar="<GAS_PRICE>", help="The gas price"
    )
    executor_env_config_group.add_argument(
        "--block-base-fee-per-gas", metavar="<FEE>", help="The base fee in a block"
    )
    executor_env_config_group.add_argument(
        "--tx-origin", metavar="<ADDRESS>", help="The transaction origin"
    )
    executor_env_config_group.add_argument(
        "--block-coinbase", metavar="<ADDRESS>", help="The coinbase of the block"
    )
    executor_env_config_group.add_argument(
        "--block-timestamp", metavar="<TIMESTAMP>", help="The timestamp of the block"
    )
    executor_env_config_group.add_argument(
        "--block-number", metavar="<BLOCK>", help="The block number"
    )
    executor_env_config_group.add_argument(
        "--block-difficulty", metavar="<DIFFICULTY>", help="The block difficulty"
    )
    executor_env_config_group.add_argument(
        "--block-prevrandao", metavar="<PREVRANDAO>", help="The block prevrandao value."
    )
    executor_env_config_group.add_argument(
        "--block-gas-limit", metavar="<GAS_LIMIT>", help="The block gas limit"
    )
    executor_env_config_group.add_argument(
        "--memory-limit",
        metavar="<MEMORY_LIMIT>",
        help="The memory limit of the EVM in bytes",
    )

    # Cache options
    cache_options_group.add_argument(
        "--force",
        action="store_true",
        help="Clear the cache and artifacts folder and recompile",
    )

    # Build options
    build_options_group.add_argument(
        "--no-cache", action="store_true", help="Disable the cache"
    )

    # Linker options
    linker_options_group.add_argument(
        "--libraries", metavar="<LIBRARIES>", help="Set pre-linked libraries"
    )

    # Compiler options
    compiler_options_group.add_argument(
        "--ignored-error-codes",
        metavar="<ERROR_CODES>",
        help="Ignore solc warnings by error code",
    )
    compiler_options_group.add_argument(
        "--deny-warnings",
        action="store_true",
        help="Warnings will trigger a compiler error",
    )
    compiler_options_group.add_argument(
        "--no-auto-detect",
        action="store_true",
        help="Do not auto-detect the `solc` version",
    )
    compiler_options_group.add_argument(
        "--use",
        metavar="<SOLC_VERSION>",
        help="Specify the solc version, or a path to a local solc, to build with.",
    )
    compiler_options_group.add_argument(
        "--offline", action="store_true", help="Do not access the network."
    )
    compiler_options_group.add_argument(
        "--via-ir",
        action="store_true",
        help="Use the Yul intermediate representation compilation pipeline",
    )
    compiler_options_group.add_argument(
        "--silent", action="store_true", help="Don't print anything on startup"
    )
    compiler_options_group.add_argument(
        "--evm-version", metavar="<VERSION>", help="The target EVM version"
    )
    compiler_options_group.add_argument(
        "--optimize", action="store_true", help="Activate the Solidity optimizer"
    )
    compiler_options_group.add_argument(
        "--optimizer-runs", metavar="<RUNS>", help="The number of optimizer runs"
    )
    compiler_options_group.add_argument(
        "--extra-output",
        metavar="<SELECTOR>",
        nargs="+",
        help="Extra output to include in the contract's artifact.",
    )
    compiler_options_group.add_argument(
        "--extra-output-files",
        metavar="<SELECTOR>",
        nargs="+",
        help="Extra output to write to separate files.",
    )

    # Project options
    project_options_group.add_argument(
        "-o",
        "--out",
        metavar="<PATH>",
        help="The path to the contract artifacts folder",
    )
    project_options_group.add_argument(
        "--revert-strings", metavar="<REVERT>", help="Revert string configuration."
    )
    project_options_group.add_argument(
        "--build-info", action="store_true", help="Generate build info files"
    )
    project_options_group.add_argument(
        "--build-info-path",
        metavar="<PATH>",
        help="Output path to directory that build info files will be written to",
    )
    project_options_group.add_argument(
        "--root", metavar="<PATH>", help="The project's root path."
    )
    project_options_group.add_argument(
        "-C", "--contracts", metavar="<PATH>", help="The contracts source directory"
    )
    project_options_group.add_argument(
        "-R", "--remappings", metavar="<REMAPPINGS>", help="The project's remappings"
    )
    project_options_group.add_argument(
        "--remappings-env",
        metavar="<ENV>",
        help="The project's remappings from the environment",
    )
    project_options_group.add_argument(
        "--cache-path", metavar="<PATH>", help="The path to the compiler cache"
    )
    project_options_group.add_argument(
        "--lib-paths", metavar="<PATH>", help="The path to the library folder"
    )
    project_options_group.add_argument(
        "--hardhat", action="store_true", help="Use the Hardhat-style project layout."
    ).aliases = ["hh"]
    project_options_group.add_argument(
        "--config-path", metavar="<FILE>", help="Path to the config file"
    )

    # Watch options
    watch_options_group.add_argument(
        "-w",
        "--watch",
        metavar="<PATH>",
        nargs="*",
        help="Watch the given files or directories for changes.",
    )
    watch_options_group.add_argument(
        "--no-restart",
        action="store_true",
        help="Do not restart the command while it's still running",
    )
    watch_options_group.add_argument(
        "--run-all",
        action="store_true",
        help="Explicitly re-run all tests when a change is made.",
    )
    watch_options_group.add_argument(
        "--watch-delay", metavar="<DELAY>", help="File update debounce delay."
    )
