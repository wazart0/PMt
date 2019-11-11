docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt down
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt build
docker-compose.exe -f ./backend/docker-compose_develop.yml -p pmt up -d

Start-Sleep -Second 10
docker.exe exec -it pmt_backend_1 python3 ./backend/restServer/initialize/createExampleUsers.py
docker.exe exec -it pmt_backend_1 python3 ./backend/restServer/initialize/createExampleGroups.py

# docker.exe logs -f -t pmt_backend_1