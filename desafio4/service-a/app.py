from flask import Flask, jsonify, request
import logging
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

users_db = {
    "1": {
        "id": "1",
        "name": "Alice Silva",
        "email": "alice.silva@email.com",
        "role": "developer",
        "active_since": "2023-01-15",
        "department": "Engineering",
        "status": "active"
    },
    "2": {
        "id": "2",
        "name": "Bruno Santos",
        "email": "bruno.santos@email.com",
        "role": "designer",
        "active_since": "2023-03-20",
        "department": "Design",
        "status": "active"
    },
    "3": {
        "id": "3",
        "name": "Carla Oliveira",
        "email": "carla.oliveira@email.com",
        "role": "manager",
        "active_since": "2022-11-10",
        "department": "Management",
        "status": "active"
    },
    "4": {
        "id": "4",
        "name": "Daniel Costa",
        "email": "daniel.costa@email.com",
        "role": "developer",
        "active_since": "2023-06-01",
        "department": "Engineering",
        "status": "active"
    },
    "5": {
        "id": "5",
        "name": "Elena Ferreira",
        "email": "elena.ferreira@email.com",
        "role": "analyst",
        "active_since": "2023-02-28",
        "department": "Data",
        "status": "inactive"
    }
}

@app.route('/')
def home():
    return jsonify({
        "service": "Users Service (Microsserviço A)",
        "version": "1.0.0",
        "description": "Gerenciamento de usuários",
        "endpoints": {
            "GET /": "Informações do serviço",
            "GET /health": "Health check",
            "GET /users": "Lista todos os usuários",
            "GET /users/<id>": "Busca usuário por ID",
            "POST /users": "Cria novo usuário",
            "PUT /users/<id>": "Atualiza usuário",
            "DELETE /users/<id>": "Remove usuário",
            "GET /stats": "Estatísticas do serviço"
        }
    }), 200

@app.route('/health')
def health():
    return jsonify({
        "service": "users-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_users": len(users_db)
    }), 200

@app.route('/users', methods=['GET'])
def get_users():
    status_filter = request.args.get('status')
    department_filter = request.args.get('department')
    
    users = list(users_db.values())
    
    if status_filter:
        users = [u for u in users if u['status'] == status_filter]
    if department_filter:
        users = [u for u in users if u['department'] == department_filter]
    
    logger.info(f"✓ Listando {len(users)} usuários")
    
    return jsonify({
        "total": len(users),
        "users": users
    }), 200

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users_db.get(user_id)
    
    if user:
        logger.info(f"✓ Usuário {user_id} encontrado")
        return jsonify(user), 200
    else:
        logger.warning(f"✗ Usuário {user_id} não encontrado")
        return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    required_fields = ['name', 'email', 'role', 'department']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    user_id = str(uuid.uuid4())[:8]
    
    new_user = {
        "id": user_id,
        "name": data['name'],
        "email": data['email'],
        "role": data['role'],
        "active_since": datetime.now().strftime('%Y-%m-%d'),
        "department": data['department'],
        "status": data.get('status', 'active')
    }
    
    users_db[user_id] = new_user
    logger.info(f"✓ Novo usuário criado: {user_id} - {data['name']}")
    
    return jsonify({
        "message": "User created successfully",
        "user": new_user
    }), 201

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    user = users_db[user_id]
    
    updatable_fields = ['name', 'email', 'role', 'department', 'status']
    for field in updatable_fields:
        if field in data:
            user[field] = data[field]
    
    logger.info(f"✓ Usuário {user_id} atualizado")
    
    return jsonify({
        "message": "User updated successfully",
        "user": user
    }), 200

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404
    
    user = users_db.pop(user_id)
    logger.info(f"✓ Usuário {user_id} removido")
    
    return jsonify({
        "message": "User deleted successfully",
        "user": user
    }), 200

@app.route('/stats')
def get_stats():
    users = list(users_db.values())
    
    active_users = len([u for u in users if u['status'] == 'active'])
    inactive_users = len([u for u in users if u['status'] == 'inactive'])
    
    departments = {}
    for user in users:
        dept = user['department']
        departments[dept] = departments.get(dept, 0) + 1
    
    roles = {}
    for user in users:
        role = user['role']
        roles[role] = roles.get(role, 0) + 1
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "total_users": len(users),
        "active_users": active_users,
        "inactive_users": inactive_users,
        "by_department": departments,
        "by_role": roles
    }), 200

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Iniciando Microsserviço de Usuários (Service A)")
    logger.info("Porta: 5001")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
