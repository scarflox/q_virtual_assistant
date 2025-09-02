# Go to project root
Set-Location "F:\q_virtual_assistant"

# Enable script execution (optional if policy is restrictive)
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Activate venv
& ".\.venv\Scripts\Activate.ps1"

# Run script and pause to see errors
python ".\test.py"
Write-Host "`nPress any key to exit..."
$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
