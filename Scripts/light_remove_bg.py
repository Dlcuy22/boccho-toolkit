"""
This script provides background removal functionality using the rembg library.
It scans a source directory for images, processes them to remove backgrounds,
and saves the results to a target directory.

Functions:
- process_images: Iterates through the input directory and removes backgrounds from image files.
- main: Orchestrates the directory setup and calls the processing function.

upon fresh run it will download the u2net.onnx model about 176Mb
"""

import os
from pathlib import Path
from rembg import remove, new_session
from PIL import Image


def process_images(input_dir: Path, output_dir: Path):
    # Initialize a rembg session for better performance in batch processing
    session = new_session()

    # Supported image extensions
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

    # Get list of files
    files = [
        f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in extensions
    ]

    if not files:
        print(f"No valid image files found in {input_dir}")
        return

    print(f"Processing {len(files)} images...")

    for i, file_path in enumerate(files, 1):
        try:
            output_path = output_dir / f"{file_path.stem}.png"

            # Skip if already processed
            if output_path.exists():
                print(f"[{i}/{len(files)}] Skipping existing: {file_path.name}")
                continue

            print(f"[{i}/{len(files)}] Removing background: {file_path.name}")

            input_image = Image.open(file_path)
            output_image = remove(input_image, session=session)
            output_image.save(output_path)

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")


def main():
    # Define paths
    input_path = Path("input/raw_frames")
    output_path = Path("output/no_bg_frames")

    # Ensure directories exist
    if not input_path.exists():
        print(f"Input directory not found: {input_path}")
        return

    output_path.mkdir(parents=True, exist_ok=True)

    process_images(input_path, output_path)
    print("Background removal complete.")


if __name__ == "__main__":
    main()
