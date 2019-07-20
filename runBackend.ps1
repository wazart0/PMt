docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt-backend_release down
docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt-backend_release build
docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt-backend_release up -d