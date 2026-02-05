"""
Main orchestrator script for Boccho ToolkitX.
Provides a CLI to run various tools (background removal, outlining, packing, cleaning).

Usage:
    python main.py remove-bg
    python main.py apply-outline
    python main.py pack <filename>
    python main.py clean
"""

import argparse
import sys
import subprocess
import shutil
from pathlib import Path


def run_script(script_name, script_args=None):
    """
    Executes a python script located in the Scripts directory.
    """
    if script_args is None:
        script_args = []

    script_path = Path("Scripts") / script_name
    if not script_path.exists():
        print(f"Error: Script '{script_path}' not found.")
        return

    # Use the current python interpreter to run the script
    cmd = [sys.executable, str(script_path)] + script_args

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def clean_directory(path: Path):
    """
    Removes all contents of a directory without removing the directory itself.
    """
    if not path.exists():
        print(f"Directory not found (skipping): {path}")
        return

    print(f"Cleaning content of: {path}")
    for item in path.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            print(f"Failed to delete {item}: {e}")


def handle_clean():
    """
    Cleans the specified input and output directories.
    """
    dirs_to_clean = [
        "output/outlined_frames",
        "output/no_bg_frames",
        "input/raw_frames",
    ]

    print("Starting clean operation...")
    for d in dirs_to_clean:
        clean_directory(Path(d))
    print("Clean operation complete.")


def main():
    parser = argparse.ArgumentParser(description="Boccho ToolkitX CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: remove-bg
    subparsers.add_parser(
        "remove-bg", help="Remove backgrounds from images in input/raw_frames"
    )

    # Command: remove-bg-simple
    subparsers.add_parser(
        "remove-bg-simple", help="Open GUI for color-based background removal"
    )

    # Command: apply-outline
    subparsers.add_parser(
        "apply-outline",
        help="Apply outline to transparent images in output/no_bg_frames",
    )

    # Command: pack
    pack_parser = subparsers.add_parser(
        "pack", help="Pack outlined frames into a .bfk archive"
    )
    pack_parser.add_argument("output_name", help="Output filename (e.g. character.bfk)")

    # Command: clean
    subparsers.add_parser(
        "clean", help="Remove content of input and output directories"
    )

    args = parser.parse_args()

    if args.command == "remove-bg":
        run_script("light_remove_bg.py")
    elif args.command == "remove-bg-simple":
        run_script("noai_rembg.py")
    elif args.command == "apply-outline":
        run_script("apply_outline.py")
    elif args.command == "pack":
        run_script("pack.py", [args.output_name])
    elif args.command == "clean":
        handle_clean()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
