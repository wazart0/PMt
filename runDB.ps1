./network/createNetwork.ps1
docker-compose -f ./db/docker-compose.yml -p pmt down
docker-compose -f ./db/docker-compose.yml -p pmt build
docker-compose -f ./db/docker-compose.yml -p pmt up -d

Remove-Item -Recurse -exclude __init__.py ./backend/app/*/migrations/*

