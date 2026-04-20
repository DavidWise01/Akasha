# close-bit265_5.ps1
# Closing region 265.5 - that's 10.5 past a byte, definitely in the weeds

Write-Host "Closing region 265.5..." -ForegroundColor Red

try { docker version | Out-Null } catch {
    Write-Host "Docker not running. Nothing to close." -ForegroundColor Yellow
    exit
}

$running = docker ps -q
if ($running) {
    Write-Host "Stopping $($running.Count) containers..."
    docker stop $running
}

$all = docker ps -aq
if ($all) {
    Write-Host "Removing $($all.Count) containers..."
    docker rm $all -f | Out-Null
}

docker system prune -af --volumes
Write-Host "Region 265.5 closed. Garden cleared." -ForegroundColor Green
