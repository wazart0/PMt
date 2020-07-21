./network/createNetwork.ps1
docker-compose.exe -f ./db/docker-compose.yml -p pmt down
docker-compose.exe -f ./db/docker-compose.yml -p pmt build
docker-compose.exe -f ./db/docker-compose.yml -p pmt up -d

Remove-Item -Recurse -exclude __init__.py ./backend/app/*/migrations/*

