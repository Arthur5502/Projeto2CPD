#!/bin/bash

# Script para parar e limpar recursos do Desafio 3

echo "==========================================================="
echo "Parando Desafio 3 - Docker Compose"
echo "==========================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}Escolha uma opção:${NC}"
echo "1. Parar serviços (manter volumes com dados)"
echo "2. Parar e remover tudo (incluindo volumes)"
echo ""
read -p "Opção [1-2]: " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Parando serviços...${NC}"
        docker compose down
        echo -e "\n${GREEN}✓ Serviços parados${NC}"
        echo -e "${YELLOW}Os volumes foram mantidos. Para reiniciar:${NC}"
        echo -e "  docker compose up -d"
        ;;
    2)
        echo -e "\n${YELLOW}Parando serviços e removendo volumes...${NC}"
        docker compose down -v
        echo -e "\n${GREEN}✓ Tudo removido (incluindo dados)${NC}"
        echo -e "${YELLOW}Para reiniciar do zero:${NC}"
        echo -e "  ./run.sh"
        ;;
    *)
        echo -e "\n${YELLOW}Opção inválida. Apenas parando serviços...${NC}"
        docker compose down
        ;;
esac

echo ""
echo "==========================================================="
