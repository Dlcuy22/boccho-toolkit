# run this command if this script cannot be ran:
# Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

$ErrorActionPreference = "Stop"

$venvPath = ".\.venv"
$activateScript = "$venvPath\Scripts\Activate.ps1"
$requirementsFile = ".\requirements.txt" # you can change this to other requirements
$pythonVersion = "3.10"    # requested Python version for the venv
$uvCmd = "uv"

function Ensure-UvExists {
    if (-not (Get-Command $uvCmd -ErrorAction SilentlyContinue)) {
        Write-Error "uv is not installed or not on PATH. Install uv and retry (e.g., pipx install uv or pip install --user uv)."
        exit 1
    }
}

function Ensure-Venv {
    if (Test-Path $venvPath) {
        Write-Host ".venv already exists. Skipping creation."
        return
    }

    Write-Host ".venv not found. Creating virtual environment with Python $pythonVersion using uv..."
    try {
        & $uvCmd venv --python $pythonVersion $venvPath
    }
    catch {
        Write-Error "uv failed to create the virtual environment with Python $pythonVersion. See uv output above for details."
        exit 1
    }
}

function Activate-Venv {
    if (-not (Test-Path $activateScript)) {
        Write-Error "Activation script not found: $activateScript"
        exit 1
    }

    Write-Host "Activating virtual environment..."
    . $activateScript

    Write-Host "Virtual environment activated."
    try {
        & python --version
    }
    catch {
        Write-Host "Warning: python not found in the activated environment."
    }
}

function Install-Requirements {
    if (-not (Test-Path $requirementsFile)) {
        Write-Host "requirements.txt not found. Skipping dependency installation."
        return
    }

    Write-Host "Installing dependencies from requirements.txt using uv..."
    try {
        & $uvCmd pip install -r $requirementsFile
    }
    catch {
        Write-Error "uv pip failed to install requirements. See uv output above for details."
        exit 1
    }

    Write-Host "Dependencies installed successfully."
}

# --- Main flow ---
Ensure-UvExists
Ensure-Venv
Activate-Venv
Install-Requirements
