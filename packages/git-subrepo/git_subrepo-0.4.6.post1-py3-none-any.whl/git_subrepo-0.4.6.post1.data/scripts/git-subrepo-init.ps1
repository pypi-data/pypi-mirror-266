<#
.Synopsis
set environment variable for git subrepo command

.Description
This is the `git-subrepo` powershell initialization script.
This script turns on the `git-subrepo` Git subcommand for Windows PowerShell
Just execute inside powershell.exe or another script file:

   .\git-subrepo-init.ps1
#>

$Errors = @()

Try {
    $pipx_python = Join-Path (Split-Path (Get-Item $PSCommandPath).Target) python.exe
} Catch {
    $pipx_python = "python"
}

:FindPython Do {
    ForEach ($python in @($pipx_python, 'python', 'py -3')) {
        $pyversion = (Get-Command -Name $python.Split()[0] -ErrorAction SilentlyContinue).Version
        If ($pyversion -ge [version]"3.6") {
            Break FindPython
        }
    }
    Throw "missing python executable in PATH"
} Until (TRUE)

$module_path = $(Invoke-Expression "$python -c 'import subrepo; print(subrepo.__file__)'")
if (!$module_path) { Throw "cannot find subrepo module" }
$subrepo_dir = Join-Path (Get-Item $module_path).Directory 'subrepo'

$Env:GIT_SUBREPO_ROOT = $subrepo_dir
$Env:Path += ";$(Join-Path $subrepo_dir 'lib')"
$version = $(git subrepo --version)
Write-Host "using version $version in $subrepo_dir"
