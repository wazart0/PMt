docker-compose.exe -f ./frontend/pmt-front/docker-compose.yml -p pmt-frontend down
docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt down
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt down
docker-compose.exe -f ./backend/docker-compose_pgadmin.yml -p pmt down
docker-compose.exe -f ./db/docker-compose.yml -p pmt down