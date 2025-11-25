import requests
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

SERVER_URL = "http://web-server:8080"
REQUEST_INTERVAL = 5

def make_request():
    try:
        logging.info(f"Enviando requisição para {SERVER_URL}")
        response = requests.get(SERVER_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"✓ Resposta recebida com sucesso!")
            logging.info(f"  - Mensagem: {data.get('message')}")
            logging.info(f"  - Número da requisição: {data.get('request_number')}")
            logging.info(f"  - Timestamp do servidor: {data.get('timestamp')}")
            logging.info(f"  - Nome do servidor: {data.get('server_name')}")
            return True
        else:
            logging.warning(f"✗ Resposta com status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logging.error("✗ Erro de conexão: não foi possível conectar ao servidor")
        return False
    except requests.exceptions.Timeout:
        logging.error("✗ Timeout: servidor não respondeu a tempo")
        return False
    except Exception as e:
        logging.error(f"✗ Erro inesperado: {str(e)}")
        return False

def check_health():
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Health check: {data.get('status')}")
            return True
    except:
        logging.warning("Health check falhou")
        return False

def main():
    logging.info("=" * 60)
    logging.info("Cliente HTTP iniciado")
    logging.info(f"Servidor alvo: {SERVER_URL}")
    logging.info(f"Intervalo entre requisições: {REQUEST_INTERVAL} segundos")
    logging.info("=" * 60)
    
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        logging.info(f"Tentando conectar ao servidor (tentativa {retry_count + 1}/{max_retries})...")
        if check_health():
            logging.info("✓ Servidor está pronto!")
            break
        retry_count += 1
        time.sleep(3)
    
    if retry_count == max_retries:
        logging.error("✗ Não foi possível conectar ao servidor após várias tentativas")
        return
    
    request_count = 0
    
    try:
        while True:
            request_count += 1
            logging.info(f"\n--- Requisição #{request_count} ---")
            
            success = make_request()
            
            if success:
                logging.info(f"Aguardando {REQUEST_INTERVAL} segundos para próxima requisição...")
            else:
                logging.warning(f"Requisição falhou. Tentando novamente em {REQUEST_INTERVAL} segundos...")
            
            time.sleep(REQUEST_INTERVAL)
            
    except KeyboardInterrupt:
        logging.info("\n" + "=" * 60)
        logging.info("Cliente interrompido pelo usuário")
        logging.info(f"Total de requisições realizadas: {request_count}")
        logging.info("=" * 60)

if __name__ == "__main__":
    main()
