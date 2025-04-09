```
powershell -c "irm https://astral.sh/uv/install.ps1 | more"
```

## Installing Git with PowerShell

### Using winget (Windows Package Manager)
```powershell
winget install --id Git.Git -e --source winget
```

### Using Chocolatey
```powershell
# First install Chocolatey if you don't have it
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Then install Git
choco install git -y
```

After installation, restart your terminal or PowerShell session to use Git commands.
