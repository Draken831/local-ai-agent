param([string]$Path=".\scripts",[string]$SubjectLike="*MSP AI Agent Code Signing*")
$Cert=Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -like $SubjectLike } | Sort-Object NotAfter -Descending | Select-Object -First 1
if(-not $Cert){
    # Backward compatibility with certificates created by earlier builds.
    $Cert=Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -like "*MSP Local AI Agent Code Signing*" } | Sort-Object NotAfter -Descending | Select-Object -First 1
}
if(-not $Cert){ throw "No code-signing cert found. Run .\scripts\New-CodeSigningCert.ps1 first." }
Get-ChildItem $Path -Filter *.ps1 -Recurse | ForEach-Object { Set-AuthenticodeSignature -FilePath $_.FullName -Certificate $Cert -HashAlgorithm SHA256 | Out-Host }
