docker-compose.exe -f ./frontend/vue-test/docker-compose.yml -p pmt down
docker-compose.exe -f ./frontend/vue-test/docker-compose.yml -p pmt build
docker-compose.exe -f ./frontend/vue-test/docker-compose.yml -p pmt up -d

# docker logs -f pmt_frontend_1