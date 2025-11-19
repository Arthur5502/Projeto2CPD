"""
API Gateway - Ponto único de entrada
Roteia requisições para os microsserviços apropriados
"""

from flask import Flask, jsonify, request, Response
import requests
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URLs dos microsserviços
USERS_SERVICE_URL = "http://users-service:5001"
ORDERS_SERVICE_URL = "http://orders-service:5003"

def forward_request(service_url, path, method='GET', data=None):
    """Encaminha requisição para o microsserviço apropriado"""
    url = f"{service_url}{path}"
    try:
        logger.info(f"🔀 Gateway encaminhando: {method} {url}")
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            return jsonify({"error": "Method not allowed"}), 405
        
        logger.info(f"✓ Resposta recebida: {response.status_code}")
        return Response(response.content, status=response.status_code, content_type='application/json')
        
    except requests.exceptions.ConnectionError:
        logger.error(f"✗ Erro de conexão com {service_url}")
        return jsonify({"error": f"Service unavailable", "service": service_url}), 503
    except requests.exceptions.Timeout:
        logger.error(f"✗ Timeout ao chamar {service_url}")
        return jsonify({"error": "Service timeout"}), 504
    except Exception as e:
        logger.error(f"✗ Erro: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    """Informações do API Gateway"""
    return jsonify({
        "service": "API Gateway",
        "version": "1.0.0",
        "description": "Ponto único de entrada para todos os microsserviços",
        "available_routes": {
            "GET /": "Informações do gateway",
            "GET /health": "Health check de todos os serviços",
            "GET /users": "Lista usuários (via Users Service)",
            "GET /users/<id>": "Busca usuário (via Users Service)",
            "POST /users": "Cria usuário (via Users Service)",
            "GET /orders": "Lista pedidos (via Orders Service)",
            "GET /orders/<id>": "Busca pedido (via Orders Service)",
            "POST /orders": "Cria pedido (via Orders Service)",
            "GET /users/<id>/orders": "Lista pedidos de um usuário (combina serviços)"
        },
        "backend_services": [
            {"name": "users-service", "url": USERS_SERVICE_URL},
            {"name": "orders-service", "url": ORDERS_SERVICE_URL}
        ]
    }), 200

@app.route('/health')
def health():
    """Health check agregado de todos os serviços"""
    health_status = {
        "gateway": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Verifica Users Service
    try:
        resp = requests.get(f"{USERS_SERVICE_URL}/health", timeout=5)
        health_status["services"]["users-service"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        health_status["services"]["users-service"] = "unhealthy"
    
    # Verifica Orders Service
    try:
        resp = requests.get(f"{ORDERS_SERVICE_URL}/health", timeout=5)
        health_status["services"]["orders-service"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except:
        health_status["services"]["orders-service"] = "unhealthy"
    
    # Status geral
    all_healthy = all(s == "healthy" for s in health_status["services"].values())
    overall_status = 200 if all_healthy else 503
    
    return jsonify(health_status), overall_status

# ============================
# Rotas para Users Service
# ============================

@app.route('/users', methods=['GET', 'POST'])
def users():
    """Roteia requisições de usuários para Users Service"""
    if request.method == 'GET':
        return forward_request(USERS_SERVICE_URL, '/users', 'GET')
    elif request.method == 'POST':
        return forward_request(USERS_SERVICE_URL, '/users', 'POST', request.get_json())

@app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(user_id):
    """Roteia requisições específicas de usuário"""
    return forward_request(USERS_SERVICE_URL, f'/users/{user_id}', request.method, request.get_json())

# ============================
# Rotas para Orders Service
# ============================

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    """Roteia requisições de pedidos para Orders Service"""
    if request.method == 'GET':
        # Passa query params (como user_id)
        query_string = request.query_string.decode('utf-8')
        path = f'/orders?{query_string}' if query_string else '/orders'
        return forward_request(ORDERS_SERVICE_URL, path, 'GET')
    elif request.method == 'POST':
        return forward_request(ORDERS_SERVICE_URL, '/orders', 'POST', request.get_json())

@app.route('/orders/<order_id>', methods=['GET', 'PUT', 'DELETE'])
def order_detail(order_id):
    """Roteia requisições específicas de pedido"""
    return forward_request(ORDERS_SERVICE_URL, f'/orders/{order_id}', request.method, request.get_json())

# ============================
# Endpoint Agregado (Orquestração)
# ============================

@app.route('/users/<user_id>/orders', methods=['GET'])
def user_orders(user_id):
    """
    Endpoint agregado: Combina dados de usuário e seus pedidos
    Demonstra orquestração de múltiplos serviços pelo Gateway
    """
    logger.info(f"🔄 Orquestrando requisição para usuário {user_id} e seus pedidos")
    
    # Busca usuário
    try:
        user_response = requests.get(f"{USERS_SERVICE_URL}/users/{user_id}", timeout=10)
        if user_response.status_code != 200:
            return jsonify({"error": "User not found"}), 404
        user_data = user_response.json()
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return jsonify({"error": "Could not fetch user"}), 503
    
    # Busca pedidos do usuário
    try:
        orders_response = requests.get(f"{ORDERS_SERVICE_URL}/orders?user_id={user_id}", timeout=10)
        orders_data = orders_response.json() if orders_response.status_code == 200 else {"orders": []}
    except Exception as e:
        logger.error(f"Erro ao buscar pedidos: {e}")
        orders_data = {"orders": []}
    
    # Combina informações
    result = {
        "user": user_data,
        "orders": orders_data.get("orders", []),
        "total_orders": len(orders_data.get("orders", [])),
        "aggregated_by": "api-gateway"
    }
    
    logger.info(f"✓ Dados agregados para usuário {user_id}")
    return jsonify(result), 200

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("Iniciando API Gateway")
    logger.info("Porta: 8000 (ponto único de entrada)")
    logger.info(f"Backends: Users ({USERS_SERVICE_URL}), Orders ({ORDERS_SERVICE_URL})")
    logger.info("=" * 70)
    app.run(host='0.0.0.0', port=8000, debug=False)
