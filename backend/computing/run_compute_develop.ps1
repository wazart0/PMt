docker-compose -f ./docker-compose_develop.yml -p pmt down
docker-compose -f ./docker-compose_develop.yml -p pmt build
docker-compose -f ./docker-compose_develop.yml -p pmt up -d

docker logs -f pmt_computing_1
