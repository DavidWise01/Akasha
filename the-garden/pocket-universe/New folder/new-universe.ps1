param([Parameter(Mandatory=$true)][string]$Name)
Set-Location "C:\Users\Dave\Desktop\the-garden\pocket-universe"

$usedMqtt = docker ps --format "{{.Ports}}" | Select-String "0.0.0.0:(\d+)->1883" | % { [int]$_.Matches.Groups[1].Value }
$usedHttp = docker ps --format "{{.Ports}}" | Select-String "0.0.0.0:(\d+)->8080" | % { [int]$_.Matches.Groups[1].Value }

$mqttPort = 1883; while ($usedMqtt -contains $mqttPort) { $mqttPort++ }
$httpPort = 8080; while ($usedHttp -contains $httpPort) { $httpPort++ }

@"
services:
  mqtt:
    ports: !override
      - "$mqttPort`:1883"
  attestor:
    ports: !override
      - "$httpPort`:8080"
"@ | Set-Content "docker-compose.$Name.yml" -Encoding ascii

$env:COMPOSE_PROJECT_NAME = $Name
docker compose -p $Name -f docker-compose.yml -f "docker-compose.$Name.yml" up -d

Write-Host "`nUniverse '$Name' alive: MQTT $mqttPort / HTTP $httpPort"