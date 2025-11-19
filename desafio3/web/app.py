"""
Aplicação Web (Flask) - Desafio 3
Sistema de gerenciamento de produtos com cache Redis e banco PostgreSQL
"""

from flask import Flask, jsonify, request
import psycopg2
import redis
import logging
import os
import json
from datetime import datetime

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'database': os.getenv('DB_NAME', 'productsdb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

# Configurações do Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'cache')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
CACHE_EXPIRATION = 300  # 5 minutos

# Conexões
db_conn = None
redis_client = None

def get_db_connection():
    """Obtém conexão com o banco de dados"""
    return psycopg2.connect(**DB_CONFIG)

def get_redis_client():
    """Obtém cliente Redis"""
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.before_request
def initialize_connections():
    """Inicializa conexões antes da primeira requisição"""
    global db_conn, redis_client
    if db_conn is None:
        try:
            db_conn = get_db_connection()
            logger.info("✓ Conexão com PostgreSQL estabelecida")
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
    
    if redis_client is None:
        try:
            redis_client = get_redis_client()
            redis_client.ping()
            logger.info("✓ Conexão com Redis estabelecida")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")

@app.route('/')
def home():
    """Endpoint principal"""
    return jsonify({
        "service": "Product Management API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "Esta página",
            "GET /health": "Health check",
            "GET /products": "Lista todos os produtos (usa cache)",
            "GET /products/<id>": "Busca produto por ID (usa cache)",
            "POST /products": "Cria novo produto",
            "PUT /products/<id>": "Atualiza produto",
            "DELETE /products/<id>": "Remove produto",
            "GET /stats": "Estatísticas do sistema"
        }
    }), 200

@app.route('/health')
def health():
    """Health check - verifica status de todas as dependências"""
    health_status = {
        "service": "web",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {}
    }
    
    # Verifica PostgreSQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Verifica Redis
    try:
        client = get_redis_client()
        client.ping()
        health_status["dependencies"]["cache"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["cache"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@app.route('/products', methods=['GET'])
def get_products():
    """Lista todos os produtos (com cache)"""
    cache_key = "products:all"
    
    # Tenta obter do cache
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info("✓ Produtos obtidos do cache Redis")
            return jsonify({
                "source": "cache",
                "products": json.loads(cached_data)
            }), 200
    except Exception as e:
        logger.warning(f"Erro ao acessar cache: {e}")
    
    # Busca no banco de dados
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, price, stock, created_at, updated_at
            FROM products
            ORDER BY created_at DESC
        """)
        
        products = []
        for row in cursor.fetchall():
            products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "stock": row[4],
                "created_at": row[5].isoformat(),
                "updated_at": row[6].isoformat()
            })
        
        cursor.close()
        conn.close()
        
        # Armazena no cache
        try:
            redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(products))
            logger.info("✓ Produtos armazenados no cache Redis")
        except Exception as e:
            logger.warning(f"Erro ao armazenar no cache: {e}")
        
        logger.info(f"✓ {len(products)} produtos obtidos do banco de dados")
        return jsonify({
            "source": "database",
            "products": products
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Busca produto por ID (com cache)"""
    cache_key = f"product:{product_id}"
    
    # Tenta obter do cache
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info(f"✓ Produto {product_id} obtido do cache")
            return jsonify({
                "source": "cache",
                "product": json.loads(cached_data)
            }), 200
    except Exception as e:
        logger.warning(f"Erro ao acessar cache: {e}")
    
    # Busca no banco
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, price, stock, created_at, updated_at
            FROM products
            WHERE id = %s
        """, (product_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            product = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "stock": row[4],
                "created_at": row[5].isoformat(),
                "updated_at": row[6].isoformat()
            }
            
            # Armazena no cache
            try:
                redis_client.setex(cache_key, CACHE_EXPIRATION, json.dumps(product))
            except Exception as e:
                logger.warning(f"Erro ao armazenar no cache: {e}")
            
            logger.info(f"✓ Produto {product_id} obtido do banco")
            return jsonify({
                "source": "database",
                "product": product
            }), 200
        else:
            return jsonify({"error": "Product not found"}), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/products', methods=['POST'])
def create_product():
    """Cria novo produto"""
    data = request.get_json()
    
    required_fields = ['name', 'price', 'stock']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, description, price, stock)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            data['name'],
            data.get('description', ''),
            data['price'],
            data['stock']
        ))
        
        product_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        # Invalida cache
        try:
            redis_client.delete("products:all")
            logger.info("✓ Cache de produtos invalidado")
        except Exception as e:
            logger.warning(f"Erro ao invalidar cache: {e}")
        
        logger.info(f"✓ Produto {product_id} criado com sucesso")
        return jsonify({
            "message": "Product created",
            "id": product_id
        }), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar produto: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
def get_stats():
    """Retorna estatísticas do sistema"""
    stats = {
        "timestamp": datetime.now().isoformat()
    }
    
    # Estatísticas do banco
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        stats["total_products"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(stock) FROM products")
        stats["total_stock"] = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
    except Exception as e:
        stats["database_error"] = str(e)
    
    # Estatísticas do cache
    try:
        info = redis_client.info()
        stats["cache"] = {
            "keys": redis_client.dbsize(),
            "memory_used": info.get('used_memory_human'),
            "hits": info.get('keyspace_hits', 0),
            "misses": info.get('keyspace_misses', 0)
        }
    except Exception as e:
        stats["cache_error"] = str(e)
    
    return jsonify(stats), 200

if __name__ == '__main__':
    logger.info("Iniciando aplicação web...")
    app.run(host='0.0.0.0', port=5000, debug=False)
