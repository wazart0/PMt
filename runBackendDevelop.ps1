docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt down
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt build
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt up -d

docker.exe logs -f -t pmt_backend_1