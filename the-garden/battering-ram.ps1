# battering-ram.ps1
# Stops every running Docker container except the one you name in $KeepName
# Run from PowerShell: .\battering-ram.ps1

$KeepName = "mine"   # <-- change this to your container name

Write-Host "Checking Docker..." -ForegroundColor Cyan
try {
    docker version | Out-Null
} catch {
    Write-Host "Docker daemon not running. Start Docker Desktop first." -ForegroundColor Red
    exit 1
}

$keepId = (docker ps -q -f "name=$KeepName" | Select-Object -First 1)
if (-not $keepId) {
    Write-Host "No running container named '$KeepName' found. Will stop ALL containers." -ForegroundColor Yellow
}

$all = docker ps -q
if (-not $all) {
    Write-Host "No containers running. Nothing to ram." -ForegroundColor Green
    exit 0
}

Write-Host "Battering ram engaged..." -ForegroundColor Magenta
foreach ($id in $all) {
    if ($id -ne $keepId) {
        $name = docker inspect --format '{{.Name}}' $id
        Write-Host "Stopping $name ($id)"
        docker stop $id | Out-Null
    } else {
        $name = docker inspect --format '{{.Name}}' $id
        Write-Host "Keeping $name ($id)" -ForegroundColor Green
    }
}

Write-Host "Done. Only '$KeepName' left standing." -ForegroundColor Green
