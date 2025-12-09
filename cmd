cd ~
cd CAMERA/Docker
docker load -i detyolov8.tar
docker load -i evn-data.tar
docker load -i evn-dashboard.tar
cd ..
cd Manage
docker compose --env-file ./.env up -d



