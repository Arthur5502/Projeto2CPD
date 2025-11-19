"""
Microsserviço B - Serviço Agregador
Consome dados do Serviço A e combina com informações adicionais
"""

from flask import Flask, jsonify, request
import requests
import logging
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL do Serviço A (usando nome do container na rede Docker)
SERVICE_A_URL = "http://service-a:5001"

# Dados adicionais simulados (atividades dos usuários)
user_activities = {
    "1": {"last_login": "2025-11-18 14:30:00", "total_logins": 245, "projects": 8},
    "2": {"last_login": "2025-11-18 10:15:00", "total_logins": 189, "projects": 5},
    "3": {"last_login": "2025-11-17 16:45:00", "total_logins": 312, "projects": 12},
    "4": {"last_login": "2025-11-18 09:20:00", "total_logins": 156, "projects": 6},
    "5": {"last_login": "2025-11-10 11:00:00", "total_logins": 87, "projects": 3}
}

def call_service_a(endpoint, method='GET', data=None):
    """
    Função auxiliar para fazer requisições ao Serviço A
    """
    url = f"{SERVICE_A_URL}{endpoint}"
    
    try:
        logger.info(f"📡 Chamando Serviço A: {method} {url}")
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            return None
        
        if response.status_code in [200, 201]:
            logger.info(f"✓ Resposta do Serviço A: {response.status_code}")
            return response.json()
        else:
            logger.warning(f"⚠️ Serviço A retornou: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        logger.error("✗ Erro de conexão com Serviço A")
        return None
    except requests.exceptions.Timeout:
        logger.error("✗ Timeout ao chamar Serviço A")
        return None
    except Exception as e:
        logger.error(f"✗ Erro inesperado: {e}")
        return None

@app.route('/')
def home():
    """Endpoint raiz com informações do serviço"""
    return jsonify({
        "service": "Aggregator Service (Microsserviço B)",
        "version": "1.0.0",
        "description": "Agrega dados de usuários com informações de atividade",
        "depends_on": ["service-a (Users Service)"],
        "endpoints": {
            "GET /": "Informações do serviço",
            "GET /health": "Health check",
            "GET /users-info": "Lista usuários com informações agregadas",
            "GET /users-info/<id>": "Informações completas de um usuário",
            "GET /active-users": "Lista usuários ativos com detalhes",
            "GET /user-summary/<id>": "Resumo executivo de um usuário",
            "GET /stats": "Estatísticas agregadas"
        }
    }), 200

@app.route('/health')
def health():
    """Health check - verifica também a saúde do Serviço A"""
    health_status = {
        "service": "aggregator-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {}
    }
    
    # Verifica Serviço A
    try:
        service_a_health = call_service_a('/health')
        if service_a_health:
            health_status["dependencies"]["service-a"] = "healthy"
        else:
            health_status["dependencies"]["service-a"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["dependencies"]["service-a"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@app.route('/users-info', methods=['GET'])
def get_users_info():
    """
    Lista todos os usuários com informações agregadas
    Combina dados do Serviço A com dados de atividade
    """
    # Busca usuários do Serviço A
    users_data = call_service_a('/users')
    
    if not users_data:
        return jsonify({
            "error": "Could not fetch users from Service A"
        }), 503
    
    users = users_data.get('users', [])
    
    # Agrega informações de atividade
    aggregated_users = []
    for user in users:
        user_id = user['id']
        activity = user_activities.get(user_id, {
            "last_login": "N/A",
            "total_logins": 0,
            "projects": 0
        })
        
        # Combina informações
        aggregated_user = {
            **user,  # Dados do Serviço A
            "activity": activity,  # Dados do Serviço B
            "days_active": _calculate_days_active(user['active_since']),
            "engagement_level": _calculate_engagement(activity)
        }
        
        aggregated_users.append(aggregated_user)
    
    logger.info(f"✓ Agregadas informações de {len(aggregated_users)} usuários")
    
    return jsonify({
        "total": len(aggregated_users),
        "users": aggregated_users,
        "aggregated_by": "service-b"
    }), 200

@app.route('/users-info/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """
    Busca informações completas de um usuário específico
    """
    # Busca usuário do Serviço A
    user_data = call_service_a(f'/users/{user_id}')
    
    if not user_data:
        return jsonify({
            "error": f"User {user_id} not found or Service A unavailable"
        }), 404
    
    # Busca atividade do usuário
    activity = user_activities.get(user_id, {
        "last_login": "N/A",
        "total_logins": 0,
        "projects": 0
    })
    
    # Monta resposta agregada
    complete_info = {
        "basic_info": user_data,
        "activity_info": activity,
        "computed_metrics": {
            "days_active": _calculate_days_active(user_data['active_since']),
            "engagement_level": _calculate_engagement(activity),
            "is_recent_user": _is_recent_user(user_data['active_since']),
            "average_logins_per_day": _calculate_avg_logins(
                user_data['active_since'], 
                activity['total_logins']
            )
        },
        "aggregated_at": datetime.now().isoformat()
    }
    
    logger.info(f"✓ Informações completas do usuário {user_id} agregadas")
    
    return jsonify(complete_info), 200

@app.route('/active-users', methods=['GET'])
def get_active_users():
    """
    Lista apenas usuários ativos com informações detalhadas
    """
    # Busca apenas usuários ativos do Serviço A
    users_data = call_service_a('/users?status=active')
    
    if not users_data:
        return jsonify({
            "error": "Could not fetch active users from Service A"
        }), 503
    
    users = users_data.get('users', [])
    
    # Agrega e enriquece informações
    active_users_info = []
    for user in users:
        user_id = user['id']
        activity = user_activities.get(user_id, {})
        
        active_users_info.append({
            "id": user_id,
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "department": user['department'],
            "active_since": user['active_since'],
            "last_login": activity.get('last_login', 'N/A'),
            "projects": activity.get('projects', 0),
            "engagement": _calculate_engagement(activity)
        })
    
    logger.info(f"✓ Listados {len(active_users_info)} usuários ativos")
    
    return jsonify({
        "total_active": len(active_users_info),
        "users": active_users_info
    }), 200

@app.route('/user-summary/<user_id>', methods=['GET'])
def get_user_summary(user_id):
    """
    Retorna um resumo executivo de um usuário
    """
    user_data = call_service_a(f'/users/{user_id}')
    
    if not user_data:
        return jsonify({
            "error": f"User {user_id} not found"
        }), 404
    
    activity = user_activities.get(user_id, {})
    
    summary = {
        "user_id": user_id,
        "name": user_data['name'],
        "summary": f"{user_data['name']} é {user_data['role']} no departamento de {user_data['department']}, "
                   f"ativo desde {user_data['active_since']} ({_calculate_days_active(user_data['active_since'])} dias). "
                   f"Realizou {activity.get('total_logins', 0)} logins e trabalha em {activity.get('projects', 0)} projetos. "
                   f"Nível de engajamento: {_calculate_engagement(activity)}.",
        "status": user_data['status'],
        "engagement_level": _calculate_engagement(activity)
    }
    
    logger.info(f"✓ Resumo do usuário {user_id} gerado")
    
    return jsonify(summary), 200

@app.route('/stats', methods=['GET'])
def get_aggregated_stats():
    """
    Retorna estatísticas agregadas de ambos os serviços
    """
    # Busca estatísticas do Serviço A
    service_a_stats = call_service_a('/stats')
    
    if not service_a_stats:
        return jsonify({
            "error": "Could not fetch stats from Service A"
        }), 503
    
    # Calcula estatísticas adicionais
    total_logins = sum(act.get('total_logins', 0) for act in user_activities.values())
    total_projects = sum(act.get('projects', 0) for act in user_activities.values())
    avg_projects_per_user = total_projects / len(user_activities) if user_activities else 0
    
    aggregated_stats = {
        "timestamp": datetime.now().isoformat(),
        "from_service_a": service_a_stats,
        "from_service_b": {
            "total_logins_tracked": total_logins,
            "total_projects": total_projects,
            "average_projects_per_user": round(avg_projects_per_user, 2)
        },
        "combined_insights": {
            "most_active_users": _get_most_active_users(3),
            "total_data_sources": 2
        }
    }
    
    return jsonify(aggregated_stats), 200

# Funções auxiliares

def _calculate_days_active(active_since):
    """Calcula quantos dias desde que o usuário está ativo"""
    try:
        start_date = datetime.strptime(active_since, '%Y-%m-%d')
        return (datetime.now() - start_date).days
    except:
        return 0

def _calculate_engagement(activity):
    """Calcula nível de engajamento baseado em atividade"""
    if not activity:
        return "low"
    
    total_logins = activity.get('total_logins', 0)
    projects = activity.get('projects', 0)
    
    score = (total_logins / 10) + (projects * 10)
    
    if score >= 100:
        return "high"
    elif score >= 50:
        return "medium"
    else:
        return "low"

def _is_recent_user(active_since):
    """Verifica se é um usuário recente (menos de 90 dias)"""
    days = _calculate_days_active(active_since)
    return days < 90

def _calculate_avg_logins(active_since, total_logins):
    """Calcula média de logins por dia"""
    days = _calculate_days_active(active_since)
    if days == 0:
        return 0
    return round(total_logins / days, 2)

def _get_most_active_users(limit=3):
    """Retorna os usuários mais ativos"""
    sorted_users = sorted(
        user_activities.items(),
        key=lambda x: x[1].get('total_logins', 0),
        reverse=True
    )
    return [user_id for user_id, _ in sorted_users[:limit]]

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Iniciando Microsserviço Agregador (Service B)")
    logger.info("Porta: 5002")
    logger.info("Depende de: Service A (http://service-a:5001)")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=False)
