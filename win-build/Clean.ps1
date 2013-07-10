$buildDir = "$pwd\build"
$cacheDir = "$pwd\cache"

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
if (Test-Path  ($pythonExe))
{
    DownloadFile "http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi" "python-2.7.5.msi"
    $exitCode = (Start-Process -FilePath "msiexec.exe" -ArgumentList "/x","$cacheDir\python-2.7.5.msi","TARGETDIR=$buildDir\Python27","/passive" -Wait -Passthru).ExitCode
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