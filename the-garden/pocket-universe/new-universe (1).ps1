param(
    [Parameter(Mandatory=$true)]
    [string]$Name
)

$baseDir = "C:\Users\Dave\Desktop\the-garden\pocket-universe"
Set-Location $baseDir

# find next free ports starting at 1883/8080
$usedMqtt = docker ps --format "{{.Ports}}" | Select-String "0.0.0.0:(\d+)->1883" | ForEach-Object { [int]$_.Matches[0].Groups[1].Value }
$usedHttp = docker ps --format "{{.Ports}}" | Select-String "0.0.0.0:(\d+)->8080" | ForEach-Object { [int]$_.Matches[0].Groups[1].Value }

$mqttPort = 1883
while ($usedMqtt -contains $mqttPort) { $mqttPort++ }

$httpPort = 8080
while ($usedHttp -contains $httpPort) { $httpPort++ }

# write override
$override = @"
services:
  mqtt:
    ports: !override
      - "$mqttPort:1883"
  attestor:
    ports: !override
      - "$httpPort:8080"
"@

$overrideFile = "docker-compose.$Name.yml"
$override | Set-Content $overrideFile -Encoding ascii

# start it
$env:COMPOSE_PROJECT_NAME = $Name
docker compose -p $Name -f docker-compose.yml -f $overrideFile up -d

Write-Host "`nUniverse '$Name' alive:" -ForegroundColor Green
Write-Host " MQTT: localhost:$mqttPort"
Write-Host " HTTP: http://localhost:$httpPort"
Write-Host " witness: http://localhost:$httpPort/witness`n"
