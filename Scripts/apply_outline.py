"""
This script adds a white outline to transparent images.
It scans a source directory for PNG files, applies an outline effect,
and saves the results to a target directory.

Functions:
- add_outline: Applies an outline to an RGBA image using a max filter.
- main: Handles directory configuration and iterates through image files.
"""

import os
from pathlib import Path
from PIL import Image, ImageFilter, ImageChops
from tqdm import tqdm


def add_outline(image, outline_width=10, outline_color=(255, 255, 255, 255)):
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    alpha = image.split()[3]

    # Expand the alpha channel to create the outline area
    outline = alpha
    for _ in range(outline_width):
        outline = outline.filter(ImageFilter.MaxFilter(3))

    # Create the outline image
    outline_img = Image.new("RGBA", image.size, outline_color)
    outline_img.putalpha(outline)

    # Extract only the outline part (without the original image area)
    outline_alpha = ImageChops.subtract(outline, alpha)
    outline_img.putalpha(outline_alpha)

    # Composite the original image over the outline
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result = Image.alpha_composite(result, outline_img)
    result = Image.alpha_composite(result, image)

    return result


def main():
    # Configuration
    input_folder = "output/no_bg_frames"
    output_folder = "output/outlined_frames"
    outline_width = 10
    # outline_color = (255, 255, 255, 255)

    outline_color = (220, 20, 60, 255)
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"Error: '{input_folder}' folder not found!")
        return

    image_files = sorted(input_path.glob("*.png"))

    if not image_files:
        print(f"No PNG files found in '{input_folder}'!")
        return

    print(f"Found {len(image_files)} images in {input_folder}")
    print(f"Applying {outline_width}px outline...")

    for img_path in tqdm(image_files, desc="Adding outlines"):
        try:
            img = Image.open(img_path)
            result = add_outline(img, outline_width, outline_color)

            output_file = output_path / img_path.name
            result.save(output_file, "PNG")

        except Exception as e:
            print(f"\nError processing {img_path.name}: {e}")

    print(f"\nSuccess! Outlined images saved to '{output_folder}/'")


if __name__ == "__main__":
    main()
