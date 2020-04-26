docker-compose.exe -f ./frontend/vue-test/docker-compose-develop.yml -p pmt down
docker-compose.exe -f ./frontend/vue-test/docker-compose-develop.yml -p pmt build
docker-compose.exe -f ./frontend/vue-test/docker-compose-develop.yml -p pmt up -d

docker logs -f pmt_frontend_1