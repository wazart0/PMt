docker-compose.exe -f ./frontend/pmt-front/docker-compose.yml -p pmt-frontend down
docker-compose.exe -f ./frontend/pmt-front/docker-compose.yml -p pmt-frontend build
docker-compose.exe -f ./frontend/pmt-front/docker-compose.yml -p pmt-frontend up -d