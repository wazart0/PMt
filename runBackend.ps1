docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt down
docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt build
docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt up -d