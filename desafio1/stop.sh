#!/bin/bash

# Script para parar e limpar recursos do Desafio 1

echo "======================================"
echo "Parando Desafio 1 - Containers em Rede"
echo "======================================"

NETWORK_NAME="desafio1-network"
SERVER_CONTAINER="web-server"
CLIENT_CONTAINER="http-client"

echo "Parando containers..."
docker stop $SERVER_CONTAINER $CLIENT_CONTAINER 2>/dev/null

echo "Removendo containers..."
docker rm $SERVER_CONTAINER $CLIENT_CONTAINER 2>/dev/null

echo "Removendo rede..."
docker network rm $NETWORK_NAME 2>/dev/null

echo "✓ Limpeza concluída!"
