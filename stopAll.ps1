docker-compose -f ./frontend/pmt-front/docker-compose.yml -p pmt-frontend down
docker-compose -f ./frontend/vue-test/docker-compose.yml -p pmt down
docker-compose -f ./frontend/vue-test/docker-compose-develop.yml -p pmt down
docker-compose -f ./backend/docker-compose_release.yml -p pmt down
docker-compose -f ./backend/docker-compose_develop.yml -p pmt down
docker-compose -f ./db/docker-compose_pgadmin.yml -p pmt down
docker-compose -f ./db/docker-compose.yml -p pmt down
docker network rm pmt_network