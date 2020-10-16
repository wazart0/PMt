docker-compose -f ./docker-compose_develop.yml -p pmt down
docker-compose -f ./docker-compose_develop.yml -p pmt build
docker-compose -f ./docker-compose_develop.yml -p pmt up -d

# Start-Sleep -Second 10
# docker exec -it pmt_backend_1 python3 ./app/initialize/createExampleUsers.py
# docker exec -it pmt_backend_1 python3 ./app/initialize/createExampleGroups.py
# docker exec -it pmt_backend_1 python3 ./app/initialize/createExampleJobs.py

docker logs -f -t pmt_backend_1