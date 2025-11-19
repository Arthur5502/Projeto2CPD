#!/bin/bash

# Script para demonstrar persistência de dados

echo "============================================================"
echo "Demonstração de Persistência - Desafio 2"
echo "============================================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VOLUME_NAME="desafio2-postgres-data"
NETWORK_NAME="desafio2-network"
DB_CONTAINER="postgres-db"
READER_CONTAINER="data-reader"

echo -e "\n${YELLOW}Este script demonstra que os dados persistem mesmo após${NC}"
echo -e "${YELLOW}remover o container da aplicação.${NC}"
echo -e "\n${YELLOW}Pressione ENTER para continuar...${NC}"
read

echo -e "\n${YELLOW}[1/4] Verificando se o volume de dados existe...${NC}"
if docker volume inspect $VOLUME_NAME &> /dev/null; then
    echo -e "${GREEN}✓ Volume encontrado: $VOLUME_NAME${NC}"
    
    # Mostra informações do volume
    echo -e "\n📊 Informações do volume:"
    docker volume inspect $VOLUME_NAME
else
    echo -e "${RED}✗ Volume não encontrado!${NC}"
    echo -e "${YELLOW}Execute ./run.sh primeiro para criar dados.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[2/4] Verificando containers...${NC}"
echo "Containers ativos:"
docker ps --filter "network=$NETWORK_NAME" --format "table {{.Names}}\t{{.Status}}"

echo -e "\n${YELLOW}[3/4] Construindo imagem do leitor de dados...${NC}"
docker build -t desafio2-reader ./reader

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagem construída com sucesso!${NC}"
else
    echo -e "${RED}✗ Erro ao construir imagem${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[4/4] Executando leitor de dados...${NC}"
echo -e "${YELLOW}Este container lerá os dados persistidos no volume.${NC}\n"

docker run --rm \
    --name $READER_CONTAINER \
    --network $NETWORK_NAME \
    -e DB_HOST=$DB_CONTAINER \
    -e DB_NAME=tasksdb \
    -e DB_USER=postgres \
    -e DB_PASSWORD=postgres \
    -e DB_PORT=5432 \
    desafio2-reader

echo -e "\n============================================================"
echo -e "${GREEN}✓ Demonstração de persistência concluída!${NC}"
echo "============================================================"
echo -e "\n${YELLOW}💡 Importante:${NC}"
echo "Os dados que você acabou de ver estão armazenados no volume Docker."
echo "Mesmo se removermos TODOS os containers, os dados permanecerão."
echo ""
echo "Para testar, execute:"
echo "  1. docker stop postgres-db"
echo "  2. docker rm postgres-db"
echo "  3. docker run -d --name postgres-db --network $NETWORK_NAME \\"
echo "     -v $VOLUME_NAME:/var/lib/postgresql/data postgres:15-alpine"
echo "  4. ./test-persistence.sh (novamente)"
echo ""
echo "Os mesmos dados estarão lá!"
