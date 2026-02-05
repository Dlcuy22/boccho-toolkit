# Boccho ToolkitX

**File Overview:**  
This document provides instructions for setting up and using Boccho ToolkitX, a suite of tools for processing character frames and packaging them as `.bfk` files for [boccho-desktop](https://github.com/dlcuy22/boccho-desktop).

---

## Setup

Initialize your environment by running the setup script corresponding to your operating system:

### Windows

```powershell
# For CPU-based processing
./setup_windows_cpu.ps1

# For GPU-accelerated processing (recommended for AI-based tools)
./setup_windows_gpu.ps1
```

### Linux

```bash
# For CPU-based processing
./setup_linux_cpu.sh
```

## Tools

The toolkit is managed through `main.py`, which provides a unified interface for the following functionality:

- **`remove-bg`**: Extracts foreground subjects using deep learning (`rembg`).
- **`remove-bg-simple`**: A manual GUI tool for color-based background removal using Pillow.
- **`apply-outline`**: Adds a customized outline to processed character images.
- **`pack`**: Compresses the finalized frames into a `.bfk` package.
- **`clean`**: Resets the workspace by clearing input and output directories.

## Usage Guide

Follow these steps to generate a `.bfk` package:

1.  **Prepare Input**  
    Place your raw image frames into the following directory:  
    `input/raw_frames/`

2.  **Remove Background**  
    Execute the automated background removal tool:

    ```bash
    python main.py remove-bg
    ```

    _Alternatively, use the GUI for manual removal:_

    ```bash
    python main.py remove-bg-simple
    ```

    Processed frames will be saved in `output/no_bg_frames/`.

3.  **Apply Outline**  
    Add an outline to your character:

    ```bash
    python main.py apply-outline
    ```

    Outlined images will be saved in `output/outlined_frames/`.

4.  **Create Package**  
    Pack the processed frames into a `.bfk` file:

    ```bash
    python main.py pack <package_name>.bfk
    ```

    _Example:_ `python main.py pack boccho.bfk`

5.  **Retrieve Output**  
    The final package will be available in:  
    `output/package/`
