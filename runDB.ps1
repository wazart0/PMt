.\network\createNetwork.ps1
docker-compose.exe -f ./db/docker-compose.yml -p pmt down
docker-compose.exe -f ./db/docker-compose.yml -p pmt up -d

docker-compose.exe -f ./db/docker-compose_pgadmin.yml -p pmt down
docker-compose.exe -f ./db/docker-compose_pgadmin.yml -p pmt up -d

if (Test-Path ./backend/restServer/jobs/migrations) {
    Remove-Item -r ./backend/restServer/jobs/migrations
}
if (Test-Path ./backend/restServer/ums/migrations) {
    Remove-Item -r ./backend/restServer/ums/migrations
}