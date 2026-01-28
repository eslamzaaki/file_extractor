# PowerShell script to test the File Extractor API

$apiUrl = "https://file-extractor-3mgo.vercel.app/api/extract"

# Test with a sample PDF
Write-Host "Testing PDF extraction..." -ForegroundColor Cyan
$body = @{
    fileUrl = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $body -ContentType "application/json"
    Write-Host "✅ Success!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}

Write-Host "`n---`n" -ForegroundColor Gray

# Test with a sample TXT file
Write-Host "Testing TXT extraction..." -ForegroundColor Cyan
$body = @{
    fileUrl = "https://www.learningcontainer.com/wp-content/uploads/2020/04/sample-text-file.txt"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $body -ContentType "application/json"
    Write-Host "✅ Success!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}
