from flask import Flask, jsonify, request
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

orders_db = {
    "1": {"id": "1", "user_id": "1", "product": "Laptop", "quantity": 1, "total": 5999.00, "status": "delivered"},
    "2": {"id": "2", "user_id": "1", "product": "Mouse", "quantity": 2, "total": 900.00, "status": "shipped"},
    "3": {"id": "3", "user_id": "2", "product": "Keyboard", "quantity": 1, "total": 599.00, "status": "pending"}
}

@app.route('/health')
def health():
    return jsonify({"service": "orders-service", "status": "healthy"}), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    user_id = request.args.get('user_id')
    orders = list(orders_db.values())
    if user_id:
        orders = [o for o in orders if o['user_id'] == user_id]
    logger.info(f"✓ Listando {len(orders)} pedidos")
    return jsonify({"orders": orders}), 200

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_db.get(order_id)
    if order:
        logger.info(f"✓ Pedido {order_id} encontrado")
        return jsonify(order), 200
    return jsonify({"error": "Order not found"}), 404

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    order_id = str(len(orders_db) + 1)
    new_order = {
        "id": order_id,
        "user_id": data.get('user_id'),
        "product": data.get('product'),
        "quantity": data.get('quantity', 1),
        "total": data.get('total', 0),
        "status": "pending"
    }
    orders_db[order_id] = new_order
    logger.info(f"✓ Pedido {order_id} criado")
    return jsonify(new_order), 201

if __name__ == '__main__':
    logger.info("Iniciando Orders Service (porta 5003)")
    app.run(host='0.0.0.0', port=5003, debug=False)
