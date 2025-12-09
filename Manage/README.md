
[![Generic badge](https://img.shields.io/badge/python-3.10-blue.svg?logo=python)](https://www.python.org/downloads/release/python-310/)
[![Generic badge](https://img.shields.io/badge/Fastapi-0.95.1-49bfa8.svg?logo=fastapi)](https://fastapi.tiangolo.com/lo)
[![Generic badge](https://img.shields.io/badge/Gunicorn-20.0.1-228b22.svg?logo=gunicorn)](https://gunicorn.org/)
[![Generic badge](https://img.shields.io/badge/Hydra-1.2.0-4dc1bf.svg)](https://hydra.cc/docs/intro)
[![Generic badge](https://img.shields.io/badge/docker-20.10.6-21a5ff.svg?logo=docker)](https://docs.docker.com)
[![Generic badge](https://img.shields.io/badge/docker%20compose-2.3.3-21a5ff.svg?logo=docker)](https://docs.docker.com/compose)


# MANAGE CONTAINER

# Table Of Content

- [Abstract](#abstract)
- [Run docker](#run-docker)
  - [Prepare](#prepare)
  - [Run docker compose](#run-docker-compose)


# Abstract

- Run all project containers. 
- Make sure the below docker images are available on your local machine
  - detyolov8:v1.0
  - evndata-manage:v1.0
  - evn-dashboard

# Run docker

## Prepare

- Install docker compose: You can follow the tutorial [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-22-04)
- Check information in [.env](.env)

## Run docker compose

```commandline
ocker compose --env-file ./.env up -d
```

- Check docker compose after run:

```commandline
docker compose ps
```

- Show logs:

```commandline
docker compsoe logs --tail 10
```
