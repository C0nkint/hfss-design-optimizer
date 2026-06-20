param(
    [string]$ApiRoot = (Join-Path (Split-Path -Parent $PSScriptRoot) "assets\hfss-api-master"),
    [string]$Output = ""
)

if (-not (Test-Path -LiteralPath $ApiRoot)) {
    Write-Error "API root not found: $ApiRoot"
    exit 1
}

$rows = Get-ChildItem -LiteralPath $ApiRoot -Recurse -Filter *.m | ForEach-Object {
    $file = $_
    $lines = Get-Content -LiteralPath $file.FullName
    $docSig = @($lines | Where-Object { $_ -match '^\s*%\s*function\s+' } | Select-Object -First 1)
    $implSig = @($lines | Where-Object { $_ -match '^\s*function\s+' } | Select-Object -First 1)
    $docText = if ($docSig.Count -gt 0) { [string]$docSig[0] } else { '' }
    $implText = if ($implSig.Count -gt 0) { [string]$implSig[0] } else { '' }

    [PSCustomObject]@{
        File = Resolve-Path -LiteralPath $file.FullName -Relative
        DocumentedSignature = (($docText -replace '^\s*%\s*', '').Trim())
        ImplementationSignature = (($implText -replace '^\s*', '').Trim())
    }
} | Sort-Object File

if ($Output) {
    $content = @("# HFSS API Signatures", "")
    foreach ($row in $rows) {
        $sig = if ($row.DocumentedSignature) { $row.DocumentedSignature } else { $row.ImplementationSignature }
        $content += "- ``$sig``"
        $content += "  - $($row.File)"
    }
    Set-Content -LiteralPath $Output -Value $content -Encoding UTF8
    Write-Host "Wrote $Output"
} else {
    $rows | Format-Table -AutoSize
}