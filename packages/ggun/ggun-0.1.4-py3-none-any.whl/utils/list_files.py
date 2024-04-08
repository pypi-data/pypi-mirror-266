import subprocess
import os
import re
from os.path import expanduser


def list_forge_test_strace_files(directory, show_tree, exclude_file_types=[]):
    """
    List all files in a directory that are being used by forge test.
    """
    # Define the command to be executed
    command = (
        "strace -f -e trace=%file -e read=none -e write=none forge test 2>&1"
        " | grep -E 'openat\\(.*\\.sol'"
    )
    # Change the current working directory to ~/Test_Ggun/vanilla
    cwd = expanduser(directory)

    # Run the command
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        text=True,
    )

    # Read the output
    output, _ = process.communicate()

    # Find all paths in the output and convert them to relative paths
    absolute_paths = re.findall(r"\"(.+\.sol)\"", output)
    paths = [os.path.relpath(path, cwd) for path in absolute_paths]
    paths = ["./" + path for path in paths]

    return paths




def list_git_files(directory, show_tree, exclude_file_types=[]):
    """
    List all files in a directory that are not ignored by git using `git ls-files` command.

    This function uses the `git ls-files` command to list all files that are not ignored
    by .gitignore files. It can also display the directory tree structure if requested.

    Args:
        directory (str): The root directory to list files from.
        show_tree (bool, optional): If True, prints the directory tree structure. Defaults to False.
    """
    # TODO use dulwich for ls-files, so we don't have to shell out, see https://stackoverflow.com/questions/50912696/dulwich-cheat-sheet-how-to-reproduce-git-ls-files
    try:
        file_list = []
        # Change the current working directory to the specified directory
        original_directory = os.getcwd()
        os.chdir(directory)

        # Execute `git ls-files` command to list all tracked files
        result = subprocess.check_output(
            "find . -type f \( -name '*.sol' -o -name '*.toml' \)",
            shell=True,
        ).decode("utf-8")

        # Change back to the original directory
        os.chdir(original_directory)

        files = result.split("\n")

        for file in files:
            if not any(file.endswith(ext) for ext in exclude_file_types):
                file_list.append(file)
                if show_tree:
                    depth = file.count("/")
                    folder_name = os.path.dirname(file) if "/" in file else "."
                    print(
                        "    " * depth + folder_name + "/|-- " + os.path.basename(file)
                    )
        return file_list
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"Error listing git files: {e}") from e


def test_list_git_files():
    """
    Test the list_git_files function with a known directory structure.
    """
    # Assuming the current directory has a .git and it's not empty
    directory = "../Test_Ggun/vanilla"    
    print("Testing list_git_files with show_tree=False")
    file_list = list_git_files(directory, show_tree=False)
    print(file_list)

    print("\nTesting list_git_files with show_tree=True")
    file_list = list_git_files(directory, show_tree=True)
    print(file_list)


if __name__ == "__main__":
    directory = "~/Test_Ggun/vanilla"

    # files = list_git_files(directory, show_tree=False)
    files = list_forge_test_strace_files(directory, show_tree=True)
    print(files)
