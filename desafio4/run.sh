#!/bin/bash


echo "================================================================="
echo "Desafio 4 - Microsserviços Independentes"
echo "================================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

NETWORK_NAME="desafio4-network"
SERVICE_A="service-a"
SERVICE_B="service-b"

echo -e "\n${YELLOW}[1/6] Limpando recursos anteriores...${NC}"
docker stop $SERVICE_A $SERVICE_B 2>/dev/null
docker rm $SERVICE_A $SERVICE_B 2>/dev/null
docker network rm $NETWORK_NAME 2>/dev/null
echo -e "${GREEN}✓ Limpeza concluída${NC}"

echo -e "\n${YELLOW}[2/6] Criando rede Docker...${NC}"
docker network create $NETWORK_NAME
echo -e "${GREEN}✓ Rede '$NETWORK_NAME' criada${NC}"

echo -e "\n${YELLOW}[3/6] Construindo imagem do Serviço A (Usuários)...${NC}"
docker build -t desafio4-service-a ./service-a
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagem do Serviço A construída${NC}"
else
    echo -e "${RED}✗ Erro ao construir Serviço A${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[4/6] Construindo imagem do Serviço B (Agregador)...${NC}"
docker build -t desafio4-service-b ./service-b
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Imagem do Serviço B construída${NC}"
else
    echo -e "${RED}✗ Erro ao construir Serviço B${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[5/6] Iniciando Serviço A (Usuários)...${NC}"
docker run -d \
    --name $SERVICE_A \
    --network $NETWORK_NAME \
    -p 5001:5001 \
    desafio4-service-a

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Serviço A iniciado na porta 5001${NC}"
else
    echo -e "${RED}✗ Erro ao iniciar Serviço A${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Aguardando Serviço A estar pronto...${NC}"
sleep 3

echo -e "\n${YELLOW}[6/6] Iniciando Serviço B (Agregador)...${NC}"
docker run -d \
    --name $SERVICE_B \
    --network $NETWORK_NAME \
    -p 5002:5002 \
    desafio4-service-b

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Serviço B iniciado na porta 5002${NC}"
else
    echo -e "${RED}✗ Erro ao iniciar Serviço B${NC}"
    exit 1
fi

echo -e "\n================================================================="
echo -e "${GREEN}✓ Todos os microsserviços estão rodando!${NC}"
echo -e "================================================================="

echo -e "\n${YELLOW}Status dos containers:${NC}"
docker ps --filter "network=$NETWORK_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${YELLOW}Informações da rede:${NC}"
docker network inspect $NETWORK_NAME | grep -A 10 "Containers"

echo -e "\n================================================================="
echo -e "${GREEN}TESTANDO COMUNICAÇÃO ENTRE MICROSSERVIÇOS${NC}"
echo -e "================================================================="

echo -e "\n${BLUE}1. Testando Serviço A (Usuários)...${NC}"
if curl -s http://localhost:5001/health > /dev/null; then
    echo -e "${GREEN}✓ Serviço A está respondendo${NC}"
    curl -s http://localhost:5001/health | python3 -m json.tool 2>/dev/null
else
    echo -e "${RED}✗ Serviço A não está respondendo${NC}"
fi

echo -e "\n${BLUE}2. Testando Serviço B (Agregador)...${NC}"
if curl -s http://localhost:5002/health > /dev/null; then
    echo -e "${GREEN}✓ Serviço B está respondendo${NC}"
    curl -s http://localhost:5002/health | python3 -m json.tool 2>/dev/null
else
    echo -e "${RED}✗ Serviço B não está respondendo${NC}"
fi

echo -e "\n${BLUE}3. Testando comunicação entre serviços...${NC}"
echo -e "${YELLOW}Serviço B buscando dados do Serviço A...${NC}"
sleep 2
curl -s http://localhost:5002/users-info | python3 -m json.tool | head -30

echo -e "\n================================================================="
echo -e "${GREEN}COMANDOS ÚTEIS${NC}"
echo -e "================================================================="
echo -e "${YELLOW}Testar Serviço A:${NC}"
echo -e "  curl http://localhost:5001/users"
echo -e "  curl http://localhost:5001/users/1"
echo -e ""
echo -e "${YELLOW}Testar Serviço B (que chama o A):${NC}"
echo -e "  curl http://localhost:5002/users-info"
echo -e "  curl http://localhost:5002/users-info/1"
echo -e "  curl http://localhost:5002/active-users"
echo -e "  curl http://localhost:5002/user-summary/1"
echo -e ""
echo -e "${YELLOW}Ver logs:${NC}"
echo -e "  docker logs -f $SERVICE_A"
echo -e "  docker logs -f $SERVICE_B"
echo -e ""
echo -e "${YELLOW}Testar completo:${NC}"
echo -e "  ./test-services.sh"
echo -e ""
echo -e "${YELLOW}Parar tudo:${NC}"
echo -e "  ./stop.sh"
echo -e ""

echo -e "================================================================="
echo -e "${GREEN}✓ Ambiente pronto! Execute ./test-services.sh para testes${NC}"
echo -e "================================================================="
