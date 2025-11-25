#!/bin/bash


echo "================================================================="
echo "Parando Desafio 4 - Microsserviços Independentes"
echo "================================================================="

NETWORK_NAME="desafio4-network"
SERVICE_A="service-a"
SERVICE_B="service-b"

echo "Parando containers..."
docker stop $SERVICE_A $SERVICE_B 2>/dev/null

echo "Removendo containers..."
docker rm $SERVICE_A $SERVICE_B 2>/dev/null

echo "Removendo rede..."
docker network rm $NETWORK_NAME 2>/dev/null

echo ""
echo "✓ Limpeza concluída!"
echo ""
echo "Para reiniciar: ./run.sh"
