from flask import Flask, jsonify, request
from datetime import datetime
import logging
import os

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

request_counter = 0

@app.route('/', methods=['GET'])
def home():
    global request_counter
    request_counter += 1
    
    client_ip = request.remote_addr
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    logging.info(f"Requisição #{request_counter} recebida de {client_ip}")
    
    response = {
        "status": "success",
        "message": "Servidor Web está funcionando!",
        "request_number": request_counter,
        "timestamp": timestamp,
        "client_ip": client_ip,
        "server_name": os.getenv('HOSTNAME', 'web-server')
    }
    
    return jsonify(response), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "web-server"}), 200

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify({
        "total_requests": request_counter,
        "uptime_message": "Servidor operacional"
    }), 200

if __name__ == '__main__':
    logging.info("Iniciando servidor web na porta 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)
