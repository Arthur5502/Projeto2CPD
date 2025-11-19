#!/bin/bash

echo "================================================================="
echo "Testando API Gateway - Desafio 5"
echo "================================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

GATEWAY_URL="http://localhost:8000"

echo -e "\n${BLUE}[1] Informações do Gateway:${NC}"
curl -s $GATEWAY_URL | python3 -m json.tool

echo -e "\n${BLUE}[2] Health Check (todos os serviços):${NC}"
curl -s $GATEWAY_URL/health | python3 -m json.tool

echo -e "\n${BLUE}[3] Listar usuários (via Gateway → Users Service):${NC}"
curl -s $GATEWAY_URL/users | python3 -m json.tool

echo -e "\n${BLUE}[4] Buscar usuário específico (via Gateway):${NC}"
curl -s $GATEWAY_URL/users/1 | python3 -m json.tool

echo -e "\n${BLUE}[5] Listar pedidos (via Gateway → Orders Service):${NC}"
curl -s $GATEWAY_URL/orders | python3 -m json.tool

echo -e "\n${BLUE}[6] Buscar pedidos de um usuário específico (via Gateway):${NC}"
curl -s "$GATEWAY_URL/orders?user_id=1" | python3 -m json.tool

echo -e "\n${BLUE}[7] Endpoint Agregado - Usuário + Seus Pedidos:${NC}"
echo -e "${YELLOW}(Gateway orquestra chamadas a ambos os serviços)${NC}"
curl -s $GATEWAY_URL/users/1/orders | python3 -m json.tool

echo -e "\n${BLUE}[8] Criar novo pedido via Gateway:${NC}"
curl -s -X POST $GATEWAY_URL/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": "2", "product": "Monitor", "quantity": 1, "total": 2499.00}' \
  | python3 -m json.tool

echo -e "\n================================================================="
echo -e "${GREEN}✓ Testes concluídos!${NC}"
echo -e "================================================================="
echo -e "\n${BLUE}📊 Arquitetura:${NC}"
echo -e "  Cliente → API Gateway (8000) → Users Service (5001)"
echo -e "                                → Orders Service (5003)"
