#!/bin/bash

# Script para parar e limpar recursos do Desafio 2

echo "======================================"
echo "Parando Desafio 2 - Volumes e Persistência"
echo "======================================"

VOLUME_NAME="desafio2-postgres-data"
NETWORK_NAME="desafio2-network"
DB_CONTAINER="postgres-db"
APP_CONTAINER="tasks-app"

echo "Parando containers..."
docker stop $DB_CONTAINER $APP_CONTAINER 2>/dev/null

echo "Removendo containers..."
docker rm $DB_CONTAINER $APP_CONTAINER 2>/dev/null

echo "Removendo rede..."
docker network rm $NETWORK_NAME 2>/dev/null

echo ""
echo "⚠️  O volume '$VOLUME_NAME' NÃO foi removido."
echo "Isso demonstra a persistência dos dados!"
echo ""
echo "Para ver os dados persistidos, execute: ./test-persistence.sh"
echo ""
echo "Para remover TUDO incluindo o volume (apagará os dados):"
echo "  docker volume rm $VOLUME_NAME"
