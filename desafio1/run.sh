#!/bin/bash


echo "======================================"
echo "Desafio 1 - Containers em Rede"
echo "======================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

NETWORK_NAME="desafio1-network"

SERVER_CONTAINER="web-server"
CLIENT_CONTAINER="http-client"

echo -e "\n${YELLOW}[1/5] Limpando containers e rede anteriores (se existirem)...${NC}"
docker stop $SERVER_CONTAINER $CLIENT_CONTAINER 2>/dev/null
docker rm $SERVER_CONTAINER $CLIENT_CONTAINER 2>/dev/null
docker network rm $NETWORK_NAME 2>/dev/null

echo -e "\n${YELLOW}[2/5] Criando rede Docker customizada '$NETWORK_NAME'...${NC}"
docker network create $NETWORK_NAME

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Rede criada com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao criar a rede${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[3/5] Construindo imagem do servidor web...${NC}"
docker build -t desafio1-server ./server

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagem do servidor construída com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao construir imagem do servidor${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[4/5] Construindo imagem do cliente HTTP...${NC}"
docker build -t desafio1-client ./client

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagem do cliente construída com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao construir imagem do cliente${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[5/5] Iniciando containers...${NC}"

echo -e "\nIniciando servidor web..."
docker run -d \
    --name $SERVER_CONTAINER \
    --network $NETWORK_NAME \
    -p 8080:8080 \
    desafio1-server

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Servidor iniciado com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao iniciar o servidor${NC}"
    exit 1
fi

echo -e "\nAguardando servidor estar pronto..."
sleep 3

echo -e "\nIniciando cliente HTTP..."
docker run -d \
    --name $CLIENT_CONTAINER \
    --network $NETWORK_NAME \
    desafio1-client

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cliente iniciado com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao iniciar o cliente${NC}"
    exit 1
fi

echo -e "\n======================================"
echo -e "${GREEN}✓ Todos os containers estão rodando!${NC}"
echo "======================================"

echo -e "\n${YELLOW}Informações dos containers:${NC}"
docker ps --filter "network=$NETWORK_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${YELLOW}Informações da rede:${NC}"
docker network inspect $NETWORK_NAME | grep -A 10 "Containers"

echo -e "\n${YELLOW}Comandos úteis:${NC}"
echo "  - Ver logs do servidor:  docker logs -f $SERVER_CONTAINER"
echo "  - Ver logs do cliente:   docker logs -f $CLIENT_CONTAINER"
echo "  - Testar servidor:       curl http://localhost:8080"
echo "  - Parar containers:      docker stop $SERVER_CONTAINER $CLIENT_CONTAINER"
echo "  - Ver rede:              docker network inspect $NETWORK_NAME"

echo -e "\n${YELLOW}Acompanhando logs (Ctrl+C para sair)...${NC}"
echo "======================================"
docker logs -f $CLIENT_CONTAINER
