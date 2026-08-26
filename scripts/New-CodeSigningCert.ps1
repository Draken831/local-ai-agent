param([string]$Subject="CN=MSP Local AI Agent Code Signing",[string]$ExportPath=".\certs\MSP-Local-Agent-CodeSigning.cer")
New-Item -ItemType Directory -Path (Split-Path $ExportPath -Parent) -Force | Out-Null
$Cert=New-SelfSignedCertificate -Type CodeSigningCert -Subject $Subject -CertStoreLocation "Cert:\CurrentUser\My" -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 -HashAlgorithm SHA256
Export-Certificate -Cert $Cert -FilePath $ExportPath | Out-Null
Write-Host "Created code signing certificate: $($Cert.Thumbprint)" -ForegroundColor Green
Write-Host "Exported: $ExportPath"
