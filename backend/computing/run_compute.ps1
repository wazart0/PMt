docker-compose -f ./docker-compose.yml -p pmt down
docker-compose -f ./docker-compose.yml -p pmt build
docker-compose -f ./docker-compose.yml -p pmt up -d
