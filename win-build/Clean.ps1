$buildDir = "$pwd\build"
$cacheDir = "$pwd\cache"
$tempDir = "$env:temp\warden"

$webclient = New-Object System.Net.WebClient

Function DownloadFile($url, $filename)
{
    $file = "$cacheDir\$filename"

    if (!(Test-Path  ($file)))
    {
        $webclient.DownloadFile($url,$file)
    }
}

if (!(Test-Path  ($tempDir)))
{
    New-Item $tempDir -type directory
}

$pythonExe = "$buildDir\Python27\python.exe"
if (Test-Path  ($pythonExe))
{
    DownloadFile "http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi" "python-2.7.5.msi"
    Copy-Item "$cacheDir\python-2.7.5.msi" "$tempDir"
    $exitCode = (Start-Process -FilePath "msiexec.exe" -ArgumentList "/x","$tempDir\python-2.7.5.msi","TARGETDIR=$buildDir\Python27","/passive" -Wait -Passthru).ExitCode
    Write-Host "Exit code was: $exitCode"
}

$pythonDir = "$buildDir\Python27"
if (Test-Path  ($pythonDir))
{
    Remove-Item -Recurse -Force $pythonDir
}

$wardenDir = "$buildDir\warden"
if (Test-Path  ($wardenDir))
{
    Remove-Item -Recurse -Force $wardenDir
}

if (Test-Path  ($tempDir))
{
    Remove-Item -Recurse -Force $tempDir
}