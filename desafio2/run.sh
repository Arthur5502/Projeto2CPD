#!/bin/bash

# Script para executar o Desafio 2 - Volumes e Persistência

echo "======================================"
echo "Desafio 2 - Volumes e Persistência"
echo "======================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VOLUME_NAME="desafio2-postgres-data"
NETWORK_NAME="desafio2-network"
DB_CONTAINER="postgres-db"
APP_CONTAINER="tasks-app"

echo -e "\n${YELLOW}[1/6] Limpando recursos anteriores...${NC}"
docker stop $DB_CONTAINER $APP_CONTAINER 2>/dev/null
docker rm $DB_CONTAINER $APP_CONTAINER 2>/dev/null
docker network rm $NETWORK_NAME 2>/dev/null

echo -e "\n${YELLOW}[2/6] Criando volume Docker para persistência...${NC}"
docker volume create $VOLUME_NAME

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Volume criado: $VOLUME_NAME${NC}"
    docker volume inspect $VOLUME_NAME | grep Mountpoint
else
    echo -e "${RED}✗ Erro ao criar volume${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[3/6] Criando rede Docker...${NC}"
docker network create $NETWORK_NAME
echo -e "${GREEN}✓ Rede criada: $NETWORK_NAME${NC}"

echo -e "\n${YELLOW}[4/6] Iniciando container PostgreSQL com volume...${NC}"
docker run -d \
    --name $DB_CONTAINER \
    --network $NETWORK_NAME \
    -e POSTGRES_DB=tasksdb \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -v $VOLUME_NAME:/var/lib/postgresql/data \
    -p 5432:5432 \
    postgres:15-alpine

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL iniciado com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao iniciar PostgreSQL${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[5/6] Construindo imagem da aplicação...${NC}"
docker build -t desafio2-app ./app

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagem construída com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao construir imagem${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[6/6] Aguardando PostgreSQL inicializar...${NC}"
sleep 5

echo -e "\n${YELLOW}Iniciando aplicação de tarefas...${NC}"
docker run -it \
    --name $APP_CONTAINER \
    --network $NETWORK_NAME \
    -e DB_HOST=$DB_CONTAINER \
    -e DB_NAME=tasksdb \
    -e DB_USER=postgres \
    -e DB_PASSWORD=postgres \
    -e DB_PORT=5432 \
    desafio2-app

echo -e "\n${GREEN}✓ Aplicação finalizada${NC}"
