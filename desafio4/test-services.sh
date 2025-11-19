#!/bin/bash

# Script para testar comunicação entre microsserviços

echo "================================================================="
echo "Testando Comunicação entre Microsserviços - Desafio 4"
echo "================================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_A_URL="http://localhost:5001"
SERVICE_B_URL="http://localhost:5002"

echo -e "\n${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}PARTE 1: Testando Serviço A (Usuários) - Independente${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}[1] Listar todos os usuários:${NC}"
curl -s $SERVICE_A_URL/users | python3 -m json.tool

echo -e "\n${BLUE}[2] Buscar usuário específico (ID: 1):${NC}"
curl -s $SERVICE_A_URL/users/1 | python3 -m json.tool

echo -e "\n${BLUE}[3] Estatísticas do Serviço A:${NC}"
curl -s $SERVICE_A_URL/stats | python3 -m json.tool

echo -e "\n${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}PARTE 2: Testando Serviço B (Agregador) - Consome A${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}[4] Usuários com informações agregadas:${NC}"
echo -e "${YELLOW}(Serviço B busca do Serviço A e adiciona dados de atividade)${NC}"
curl -s $SERVICE_B_URL/users-info | python3 -m json.tool | head -50

echo -e "\n${BLUE}[5] Informações completas de um usuário:${NC}"
echo -e "${YELLOW}(Combina dados de ambos os serviços)${NC}"
curl -s $SERVICE_B_URL/users-info/1 | python3 -m json.tool

echo -e "\n${BLUE}[6] Apenas usuários ativos:${NC}"
curl -s $SERVICE_B_URL/active-users | python3 -m json.tool | head -40

echo -e "\n${BLUE}[7] Resumo executivo de um usuário:${NC}"
curl -s $SERVICE_B_URL/user-summary/1 | python3 -m json.tool

echo -e "\n${BLUE}[8] Estatísticas agregadas:${NC}"
curl -s $SERVICE_B_URL/stats | python3 -m json.tool

echo -e "\n${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}PARTE 3: Demonstração de Comunicação HTTP${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Visualizando logs do Serviço B (últimas 20 linhas):${NC}"
echo -e "${YELLOW}Observe as requisições HTTP para o Serviço A:${NC}"
docker logs service-b 2>&1 | tail -20

echo -e "\n================================================================="
echo -e "${GREEN}✓ Testes concluídos!${NC}"
echo -e "================================================================="

echo -e "\n${BLUE}📊 Resumo da Comunicação:${NC}"
echo -e "  1. Serviço A (porta 5001) - Fornece dados de usuários"
echo -e "  2. Serviço B (porta 5002) - Consome Serviço A via HTTP"
echo -e "  3. Comunicação através da rede Docker 'desafio4-network'"
echo -e "  4. Serviço B agrega dados adicionais aos dados do Serviço A"
echo -e ""
echo -e "${BLUE}🔗 Fluxo de Dados:${NC}"
echo -e "  Cliente → Serviço B → Serviço A (via HTTP) → Serviço B → Cliente"
echo -e ""
