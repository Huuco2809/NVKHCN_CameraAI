[![Generic badge](https://img.shields.io/badge/python-3.10-blue.svg?logo=python)](https://www.python.org/downloads/release/python-310/)
[![Generic badge](https://img.shields.io/badge/Fastapi-0.95.1-49bfa8.svg?logo=fastapi)](https://fastapi.tiangolo.com/lo)
[![Generic badge](https://img.shields.io/badge/Gunicorn-20.0.1-228b22.svg?logo=gunicorn)](https://gunicorn.org/)
[![Generic badge](https://img.shields.io/badge/Hydra-1.2.0-4dc1bf.svg)](https://hydra.cc/docs/intro)
[![Generic badge](https://img.shields.io/badge/docker-20.10.6-21a5ff.svg?logo=docker)](https://docs.docker.com)
[![Generic badge](https://img.shields.io/badge/docker%20compose-2.3.3-21a5ff.svg?logo=docker)](https://docs.docker.com/compose)


# DATA MANAGE

# Table Of Content

- [Abstract](#abstract)
- [Build docker](#build-docker)
- [Run docker](#run-docker)
  - [Prepare](#prepare)
  - [Run docker compose](#run-docker-compose)


# Abstract

- Source include two task:
  - Background task: 
    - Get camera: Read rtsp camera, using multiprocessing and multithreading
    - Processing image: Detection, Check object, Crop object, Tracking (Optional)
    - Update database: Create, Insert information into database. (MongoDB)
  - API task: The API documentation after running the server can be viewed at `http://<HOST>:<PORT>/docs`. The API provides several endpoints for interacting with the database from the dashboard.

# Build docker

```commandline
sudo docker build -f Dockerfile -t evndata-manage:v1.0 .
```

# Run docker

## Prepare

- Install docker compose: You can follow the tutorial [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)
- Check list camera rtsp at [cameras.json](cfg/cameras.json). Each camera config include tow information:
  - rtsp: rtsp link
  - max_fps: Expected maximum fps when reading and processing the camera. (this value will be used when have_object is true, otherwise, fps is 2)
- Check information in docker-compose.yaml

  ```yaml
  db-manage-background:
    command: python3.10 background.py updateDb_api.detector.host=http://10.0.0.238
  ```
    
  `updateDb_api.detector.host` being the detection server address.

  ```yaml
  db-manage-api:
    command: >
      gunicorn 'server:main("data_api.server_public.host=http://10.0.0238 data_api.server_public.port=8030")'
      --bind :8030 --workers 4 --worker-class uvicorn.workers.UvicornWorker
    ports:
      - "8030:8030"
  ```
    
  ***In this config***
  - command: `data_api.server_public.host` and `data_api.server_public.host` are server information, that can be accessed from outside.
  - ports: we will run the server at port `8030` inside the docker-container and expose it at `8030` for access from outside docker-container    
        

## Run docker compose

```commandline
docker compose up -d
```

- Check docker compose after run:

```commandline
docker compose ps
```

- Show logs:

```commandline
docker compsoe logs --tail 10
```
