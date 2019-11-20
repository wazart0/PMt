docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt down
docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt build
docker-compose.exe -f ./backend/docker-compose_release.yml -p pmt up -d

Start-Sleep -Second 10
docker.exe exec -it pmt_backend_1 python3 ./initialize/createExampleUsers.py
docker.exe exec -it pmt_backend_1 python3 ./initialize/createExampleGroups.py
docker.exe exec -it pmt_backend_1 python3 ./initialize/createExampleJobs.py