docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt-backend_release down
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt-backend_develop down
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt-backend_develop build
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt-backend_develop up