#!/bin/bash

echo "================================================================="
echo "Desafio 5 - Microsserviços com API Gateway"
echo "================================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}Iniciando todos os serviços com Docker Compose...${NC}"
docker compose up -d --build

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Todos os serviços iniciados!${NC}"
else
    echo -e "\n${RED}✗ Erro ao iniciar serviços${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Aguardando serviços estarem prontos...${NC}"
sleep 5

echo -e "\n================================================================="
echo -e "${GREEN}STATUS DOS SERVIÇOS${NC}"
echo -e "================================================================="
docker compose ps

echo -e "\n${GREEN}✓ API Gateway disponível em: http://localhost:8000${NC}"
echo -e "\nComandos úteis:"
echo -e "  - Ver logs: docker compose logs -f"
echo -e "  - Testar: ./test-gateway.sh"
echo -e "  - Parar: ./stop.sh"
