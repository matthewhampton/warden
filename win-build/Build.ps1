$buildDir = "C:\warden-build"
$cacheDir = "$pwd\cache"
$tempDir = "$env:temp\warden"

if (!(Test-Path  ($buildDir)))
{
    New-Item $buildDir -type directory
}

if (!(Test-Path  ($tempDir)))
{
    New-Item $tempDir -type directory
}

if (!(Test-Path  ($cacheDir)))
{
    New-Item $cacheDir -type directory
}

$webclient = New-Object System.Net.WebClient

Function DownloadFile($url, $filename)
{
    $file = "$cacheDir\$filename"

    if (!(Test-Path  ($file)))
    {
        $webclient.DownloadFile($url,$file)
    }
}

$pythonExe = "$buildDir\Python27\python.exe"
if (!(Test-Path  ($pythonExe)))
{
    DownloadFile "http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi" "python-2.7.5.msi"
    Copy-Item "$cacheDir\python-2.7.5.msi" "$tempDir"
    $exitCode = (Start-Process -FilePath "msiexec.exe" -ArgumentList "/i","$tempDir\python-2.7.5.msi","TARGETDIR=$buildDir\Python27","/passive" -Wait -Passthru).ExitCode
    Write-Host "Exit code was: $exitCode"
}

$easyInstallExe = "$buildDir\Python27\Scripts\easy_install.exe"
if (!(Test-Path  ($easyInstallExe)))
{
    DownloadFile "http://python-distribute.org/distribute_setup.py" "distribute_setup.py"
    $exitCode = (Start-Process -FilePath $pythonExe -ArgumentList "$cacheDir\distribute_setup.py" -Wait -Passthru).ExitCode
    Write-Host "Exit code was: $exitCode"
}

$pipExe = "$buildDir\Python27\Scripts\pip.exe"
if (!(Test-Path  ($pipExe)))
{
    $exitCode = (Start-Process -FilePath $easyInstallExe -ArgumentList "pip" -Wait -Passthru).ExitCode
    Write-Host "Exit code was: $exitCode"
}

$wardenInstallerExe = "$buildDir\Python27\Scripts\warden-install.exe"
if (!(Test-Path  ($wardenInstallerExe)))
{
	$wardenSource = [System.IO.Path]::GetFullPath("$pwd\..")
	Write-Host "Pip is $pipExe"
	Write-Host "Warden source location is $wardenSource"
    $exitCode = (Start-Process -FilePath $pipExe -ArgumentList "install","$wardenSource" -Wait -Passthru).ExitCode
    Write-Host "Exit code was: $exitCode"
}

$wardenDir = "$buildDir\warden"
if (!(Test-Path  ($wardenDir)))
{

    Set-Item -path env:Path -value ($env:Path + ";$buildDir\Python27;$buildDir\Python27\Scripts")
    Set-Item -path env:PIP_DOWNLOAD_CACHE -value ("$cacheDir")

    $exitCode = (Start-Process -FilePath $wardenInstallerExe -Wait -Passthru).ExitCode
    Write-Host "Exit code was: $exitCode"
}

if (Test-Path  ($tempDir))
{
    Remove-Item -Recurse -Force $tempDir
}