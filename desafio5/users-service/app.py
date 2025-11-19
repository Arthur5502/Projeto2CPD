"""
Microsserviço 1 - Users Service
Gerencia informações de usuários
"""

from flask import Flask, jsonify, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users_db = {
    "1": {"id": "1", "name": "Alice Silva", "email": "alice@email.com", "status": "active"},
    "2": {"id": "2", "name": "Bruno Santos", "email": "bruno@email.com", "status": "active"},
    "3": {"id": "3", "name": "Carla Oliveira", "email": "carla@email.com", "status": "inactive"}
}

@app.route('/health')
def health():
    return jsonify({"service": "users-service", "status": "healthy"}), 200

@app.route('/users', methods=['GET'])
def get_users():
    logger.info("✓ Listando usuários")
    return jsonify({"users": list(users_db.values())}), 200

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users_db.get(user_id)
    if user:
        logger.info(f"✓ Usuário {user_id} encontrado")
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = str(len(users_db) + 1)
    new_user = {"id": user_id, **data}
    users_db[user_id] = new_user
    logger.info(f"✓ Usuário {user_id} criado")
    return jsonify(new_user), 201

if __name__ == '__main__':
    logger.info("Iniciando Users Service (porta 5001)")
    app.run(host='0.0.0.0', port=5001, debug=False)
