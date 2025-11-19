#!/bin/bash

# Script para executar o Desafio 3 - Docker Compose

echo "==========================================================="
echo "Desafio 3 - Docker Compose Orquestrando Serviços"
echo "==========================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\n${YELLOW}[1/3] Verificando Docker e Docker Compose...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker não está instalado${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose não está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker e Docker Compose estão instalados${NC}"

echo -e "\n${YELLOW}[2/3] Limpando recursos anteriores (se existirem)...${NC}"
docker compose down -v 2>/dev/null
echo -e "${GREEN}✓ Limpeza concluída${NC}"

echo -e "\n${YELLOW}[3/3] Iniciando serviços com Docker Compose...${NC}"
echo -e "${BLUE}Este processo irá:${NC}"
echo -e "${BLUE}  1. Criar a rede desafio3-network${NC}"
echo -e "${BLUE}  2. Criar volumes para PostgreSQL e Redis${NC}"
echo -e "${BLUE}  3. Iniciar PostgreSQL (db)${NC}"
echo -e "${BLUE}  4. Iniciar Redis (cache)${NC}"
echo -e "${BLUE}  5. Construir e iniciar o serviço Web${NC}"
echo ""

docker compose up -d --build

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Todos os serviços foram iniciados com sucesso!${NC}"
else
    echo -e "\n${RED}✗ Erro ao iniciar os serviços${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Aguardando serviços estarem prontos...${NC}"
sleep 10

echo -e "\n==========================================================="
echo -e "${GREEN}STATUS DOS SERVIÇOS${NC}"
echo -e "==========================================================="
docker compose ps

echo -e "\n==========================================================="
echo -e "${GREEN}INFORMAÇÕES DA REDE${NC}"
echo -e "==========================================================="
docker network inspect desafio3-network | grep -A 5 "Containers" | head -20

echo -e "\n==========================================================="
echo -e "${GREEN}VOLUMES CRIADOS${NC}"
echo -e "==========================================================="
docker volume ls | grep desafio3

echo -e "\n==========================================================="
echo -e "${GREEN}HEALTH CHECK${NC}"
echo -e "==========================================================="

# Testa cada serviço
echo -e "\n${BLUE}Testando serviço Web...${NC}"
if curl -s http://localhost:5000/health > /dev/null; then
    echo -e "${GREEN}✓ Serviço Web está saudável${NC}"
    curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null || echo "OK"
else
    echo -e "${RED}✗ Serviço Web não está respondendo${NC}"
fi

echo -e "\n${BLUE}Testando PostgreSQL...${NC}"
if docker exec desafio3-db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL está aceitando conexões${NC}"
else
    echo -e "${RED}✗ PostgreSQL não está respondendo${NC}"
fi

echo -e "\n${BLUE}Testando Redis...${NC}"
if docker exec desafio3-cache redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis está respondendo${NC}"
else
    echo -e "${RED}✗ Redis não está respondendo${NC}"
fi

echo -e "\n==========================================================="
echo -e "${GREEN}COMANDOS ÚTEIS${NC}"
echo -e "==========================================================="
echo -e "${YELLOW}Ver logs de todos os serviços:${NC}"
echo -e "  docker compose logs -f"
echo -e ""
echo -e "${YELLOW}Ver logs de um serviço específico:${NC}"
echo -e "  docker compose logs -f web"
echo -e "  docker compose logs -f db"
echo -e "  docker compose logs -f cache"
echo -e ""
echo -e "${YELLOW}Testar a API:${NC}"
echo -e "  curl http://localhost:5000"
echo -e "  curl http://localhost:5000/products"
echo -e "  curl http://localhost:5000/stats"
echo -e ""
echo -e "${YELLOW}Parar todos os serviços:${NC}"
echo -e "  ./stop.sh"
echo -e ""
echo -e "${YELLOW}Ver status dos serviços:${NC}"
echo -e "  docker compose ps"
echo -e ""
echo -e "${YELLOW}Executar comandos em um serviço:${NC}"
echo -e "  docker compose exec db psql -U postgres -d productsdb"
echo -e "  docker compose exec cache redis-cli"
echo -e ""

echo -e "\n==========================================================="
echo -e "${GREEN}TESTAR A APLICAÇÃO${NC}"
echo -e "==========================================================="
echo -e "${BLUE}Execute o script de testes:${NC}"
echo -e "  ./test-api.sh"
echo -e ""
echo -e "${BLUE}Ou acesse no navegador:${NC}"
echo -e "  http://localhost:5000"
echo -e ""

echo -e "==========================================================="
echo -e "${GREEN}✓ Ambiente pronto para uso!${NC}"
echo -e "==========================================================="
