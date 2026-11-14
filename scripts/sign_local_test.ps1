# Self-signs dist\Win11NetSpeedCompact.exe for local testing on Windows 11
# Bypasses local Smart App Control by trusting your local publisher certificate
param (
    [string]$ExePath = ".\dist\Win11NetSpeedCompact.exe"
)

if (-not (Test-Path $ExePath)) {
    Write-Host "File not found: $ExePath. Please build it first with scripts\build_release.bat." -ForegroundColor Yellow
    exit 1
}

$certName = "Win11NetSpeedCompact Dev"
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq "CN=$certName" } | Select-Object -First 1

if (-not $cert) {
    Write-Host "Creating local self-signed developer certificate..." -ForegroundColor Cyan
    $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=$certName" -CertStoreLocation Cert:\CurrentUser\My

    $rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store "Root", "CurrentUser"
    $rootStore.Open("ReadWrite")
    $rootStore.Add($cert)
    $rootStore.Close()

    $pubStore = New-Object System.Security.Cryptography.X509Certificates.X509Store "TrustedPublisher", "CurrentUser"
    $pubStore.Open("ReadWrite")
    $pubStore.Add($cert)
    $pubStore.Close()
    Write-Host "Certificate added to Trusted Root & Trusted Publishers for CurrentUser." -ForegroundColor Green
}

Write-Host "Signing $ExePath..." -ForegroundColor Cyan
Set-AuthenticodeSignature -FilePath $ExePath -Certificate $cert -HashAlgorithm SHA256
Write-Host "Successfully signed! You can now run the EXE on this computer." -ForegroundColor Green
