docker-compose -f ./postgres/docker-compose.yml -p pmt down
docker-compose -f ./postgres/docker-compose.yml -p pmt build
docker-compose -f ./postgres/docker-compose.yml -p pmt up -d


