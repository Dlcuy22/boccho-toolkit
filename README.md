# Boccho ToolkitX

Tools for creating `.bfk` packages for [boccho-desktop](https://github.com/dlcuy22/boccho-desktop).

## Setup

Initialize the environment:

```bash
# Windows
./setup_windows_cpu.ps1

# Linux
./setup_linux_cpu.sh
```

## Usage

Place raw frames in `input/raw_frames`, then run:

```bash
# Workflow
python main.py remove-bg
python main.py apply-outline
python main.py pack <filename.bfk>

# Maintenance
python main.py clean
```
