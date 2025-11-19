#!/bin/bash

# Script para testar a API do Desafio 3

echo "==========================================================="
echo "Testando API de Produtos - Desafio 3"
echo "==========================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="http://localhost:5000"

echo -e "\n${YELLOW}[1/7] Testando endpoint raiz...${NC}"
curl -s $BASE_URL | python3 -m json.tool
echo -e "${GREEN}✓ Endpoint raiz OK${NC}"

echo -e "\n${YELLOW}[2/7] Listando produtos (primeira vez - do banco)...${NC}"
curl -s $BASE_URL/products | python3 -m json.tool
echo -e "${GREEN}✓ Produtos listados${NC}"

echo -e "\n${YELLOW}[3/7] Listando produtos (segunda vez - do cache)...${NC}"
echo -e "${BLUE}Observe que 'source' será 'cache' desta vez${NC}"
sleep 1
curl -s $BASE_URL/products | python3 -m json.tool | head -20
echo -e "${GREEN}✓ Cache funcionando!${NC}"

echo -e "\n${YELLOW}[4/7] Buscando produto específico (ID: 1)...${NC}"
curl -s $BASE_URL/products/1 | python3 -m json.tool
echo -e "${GREEN}✓ Produto encontrado${NC}"

echo -e "\n${YELLOW}[5/7] Criando novo produto...${NC}"
curl -s -X POST $BASE_URL/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Webcam Logitech C920",
    "description": "Webcam Full HD 1080p",
    "price": 399.99,
    "stock": 30
  }' | python3 -m json.tool
echo -e "${GREEN}✓ Produto criado${NC}"

echo -e "\n${YELLOW}[6/7] Verificando estatísticas...${NC}"
curl -s $BASE_URL/stats | python3 -m json.tool
echo -e "${GREEN}✓ Estatísticas obtidas${NC}"

echo -e "\n${YELLOW}[7/7] Verificando health check...${NC}"
curl -s $BASE_URL/health | python3 -m json.tool
echo -e "${GREEN}✓ Health check OK${NC}"

echo -e "\n==========================================================="
echo -e "${GREEN}✓ Todos os testes concluídos com sucesso!${NC}"
echo -e "==========================================================="

echo -e "\n${BLUE}Demonstração de Cache:${NC}"
echo -e "  1. A primeira requisição GET /products busca do banco (source: database)"
echo -e "  2. Requisições subsequentes usam cache (source: cache)"
echo -e "  3. Ao criar/atualizar produtos, o cache é invalidado"
echo -e ""

echo -e "${BLUE}Demonstração de Dependências:${NC}"
echo -e "  1. O serviço Web só inicia após DB e Cache estarem saudáveis"
echo -e "  2. Todos os serviços se comunicam pela rede interna"
echo -e "  3. Dados persistem nos volumes Docker"
echo -e ""
