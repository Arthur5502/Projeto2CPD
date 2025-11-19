"""
Leitor de Dados - Desafio 2
Este script demonstra que os dados persistem mesmo após remover o container original.
"""

import psycopg2
import time
import logging
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'tasksdb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

def wait_for_db(max_retries=30):
    """Aguarda o banco de dados estar pronto"""
    logging.info("Aguardando banco de dados estar pronto...")
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            logging.info("✓ Banco de dados está pronto!")
            return True
        except psycopg2.OperationalError:
            logging.info(f"Tentativa {attempt + 1}/{max_retries} - Aguardando...")
            time.sleep(2)
    
    return False

def read_all_tasks():
    """Lê todas as tarefas do banco de dados"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, description, status, created_at, updated_at 
        FROM tasks 
        ORDER BY created_at DESC
    """)
    
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return tasks

def read_operation_logs():
    """Lê os logs de operações"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, operation, details, timestamp 
        FROM operation_logs 
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return logs

def get_database_info():
    """Obtém informações sobre o banco de dados"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Verifica tamanho do banco
    cursor.execute("SELECT pg_database_size(current_database())")
    db_size = cursor.fetchone()[0]
    
    # Lista todas as tabelas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return {
        'size_bytes': db_size,
        'size_mb': db_size / (1024 * 1024),
        'tables': tables
    }

def main():
    """Função principal do leitor"""
    print("=" * 70)
    print("LEITOR DE DADOS PERSISTIDOS - Demonstração de Persistência")
    print("=" * 70)
    print("\nEste script lê dados que foram salvos anteriormente,")
    print("demonstrando que os dados persistem mesmo após remover containers.")
    print("=" * 70)
    
    if not wait_for_db():
        logging.error("✗ Não foi possível conectar ao banco de dados")
        return
    
    # Obtém informações do banco
    db_info = get_database_info()
    print(f"\n📊 INFORMAÇÕES DO BANCO DE DADOS")
    print(f"Tamanho: {db_info['size_mb']:.2f} MB")
    print(f"Tabelas: {', '.join(db_info['tables'])}")
    
    # Lê e exibe tarefas
    print("\n" + "=" * 70)
    print("📝 TAREFAS PERSISTIDAS")
    print("=" * 70)
    
    tasks = read_all_tasks()
    if tasks:
        for task in tasks:
            print(f"\n┌─ Tarefa ID: {task[0]}")
            print(f"│  Título: {task[1]}")
            print(f"│  Descrição: {task[2]}")
            print(f"│  Status: {task[3]}")
            print(f"│  Criada em: {task[4]}")
            print(f"└─ Atualizada em: {task[5]}")
        print(f"\n✓ Total de tarefas encontradas: {len(tasks)}")
    else:
        print("\n⚠️  Nenhuma tarefa encontrada no banco de dados.")
        print("Execute a aplicação principal primeiro para criar dados.")
    
    # Lê e exibe logs de operações
    print("\n" + "=" * 70)
    print("📋 HISTÓRICO DE OPERAÇÕES (últimas 20)")
    print("=" * 70)
    
    logs = read_operation_logs()
    if logs:
        for log in logs:
            print(f"\n[{log[3]}] {log[1]}")
            print(f"  └─ {log[2]}")
        print(f"\n✓ Total de operações registradas: {len(logs)}")
    else:
        print("\n⚠️  Nenhum log de operação encontrado.")
    
    print("\n" + "=" * 70)
    print("✓ Leitura concluída com sucesso!")
    print("=" * 70)
    print("\n💡 Os dados acima foram lidos de um volume Docker persistente.")
    print("Mesmo que os containers sejam removidos, estes dados permanecem.")
    print("=" * 70)

if __name__ == "__main__":
    main()
