"""
This script packs processed frames into a .bfk archive (zip format).
It takes an output filename as an argument, creates a directory structure
inside the archive based on that name, and compresses the contents of
the 'output/outlined_frames' directory into 'output/package'.

Functions:
- pack_frames: Compresses valid image files from the source directory into the target archive.
- main: Handles command-line arguments and script execution flow.
"""

import argparse
import zipfile
from pathlib import Path
from tqdm import tqdm


def pack_frames(output_filename: str):
    """
    Packs frames from the output directory into a .bfk zip archive.

    Args:
        output_filename (str): The name of the output archive file (e.g., 'character.bfk').
    """
    source_dir = Path("output/outlined_frames")
    # Define output directory for packages
    destination_dir = Path("output/package")
    destination_dir.mkdir(parents=True, exist_ok=True)

    output_path = destination_dir / output_filename

    # Determine internal folder name (strip extension)
    # If the user provides "character.bfk", the internal folder is "character"
    internal_folder_name = Path(output_filename).stem

    if not source_dir.exists():
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    # Get all PNG files
    files = sorted(
        [f for f in source_dir.iterdir() if f.is_file() and f.suffix.lower() == ".png"]
    )

    if not files:
        print(f"No PNG files found in '{source_dir}'.")
        return

    print(f"Packing {len(files)} frames into '{output_path}'...")
    print(f"Internal directory structure: '{internal_folder_name}/'")

    try:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in tqdm(files, desc="Archiving"):
                # Define path inside zip
                arcname = f"{internal_folder_name}/{file_path.name}"
                zf.write(file_path, arcname=arcname)

        print(f"\nSuccess! Archive created at: {output_path.absolute()}")

    except Exception as e:
        print(f"\nError creating archive: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Pack outlined frames into a .bfk archive in output/package."
    )
    parser.add_argument("output", help="Output filename (e.g., character.bfk)")

    args = parser.parse_args()
    pack_frames(args.output)


if __name__ == "__main__":
    main()
