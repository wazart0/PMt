docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt down
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt build
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt up -d

Start-Sleep -Second 10
docker exec -it pmt_backend_1 python3 ./initialize/createUsers.py

docker.exe logs -f -t pmt_backend_1