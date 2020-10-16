docker-compose -f ./docker-compose_release.yml -p pmt down
docker-compose -f ./docker-compose_release.yml -p pmt build
docker-compose -f ./docker-compose_release.yml -p pmt up -d

# Start-Sleep -Second 10
# docker exec -it pmt_backend_1 python3 ./initialize/createExampleUsers.py
# docker exec -it pmt_backend_1 python3 ./initialize/createExampleGroups.py
# docker exec -it pmt_backend_1 python3 ./initialize/createExampleJobs.py

docker logs -f pmt_backend_1