"""
Aplicação de Gerenciamento de Tarefas - Desafio 2
Demonstra persistência de dados com PostgreSQL e Docker Volumes
"""

import psycopg2
from psycopg2 import sql
import time
import logging
from datetime import datetime
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurações do banco de dados
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
    
    logging.error("✗ Não foi possível conectar ao banco de dados")
    return False

def get_db_connection():
    """Cria uma conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {e}")
        raise

def initialize_database():
    """Inicializa o banco de dados e cria as tabelas"""
    logging.info("Inicializando banco de dados...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cria a tabela de tarefas se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Cria a tabela de logs para rastrear operações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operation_logs (
            id SERIAL PRIMARY KEY,
            operation VARCHAR(50) NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logging.info("✓ Banco de dados inicializado com sucesso!")

def add_task(title, description=""):
    """Adiciona uma nova tarefa"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s) RETURNING id",
        (title, description)
    )
    task_id = cursor.fetchone()[0]
    
    # Registra a operação
    cursor.execute(
        "INSERT INTO operation_logs (operation, details) VALUES (%s, %s)",
        ("CREATE_TASK", f"Criada tarefa ID {task_id}: {title}")
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logging.info(f"✓ Tarefa '{title}' adicionada com ID {task_id}")
    return task_id

def list_tasks():
    """Lista todas as tarefas"""
    conn = get_db_connection()
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

def update_task_status(task_id, new_status):
    """Atualiza o status de uma tarefa"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE tasks SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
        (new_status, task_id)
    )
    
    # Registra a operação
    cursor.execute(
        "INSERT INTO operation_logs (operation, details) VALUES (%s, %s)",
        ("UPDATE_TASK", f"Tarefa ID {task_id} atualizada para status '{new_status}'")
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logging.info(f"✓ Tarefa ID {task_id} atualizada para status '{new_status}'")

def get_statistics():
    """Obtém estatísticas do banco de dados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Conta tarefas por status
    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM tasks 
        GROUP BY status
    """)
    status_counts = dict(cursor.fetchall())
    
    # Conta total de tarefas
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]
    
    # Conta total de operações
    cursor.execute("SELECT COUNT(*) FROM operation_logs")
    total_operations = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return {
        'total_tasks': total_tasks,
        'status_counts': status_counts,
        'total_operations': total_operations
    }

def show_menu():
    """Exibe o menu interativo"""
    print("\n" + "=" * 60)
    print("SISTEMA DE GERENCIAMENTO DE TAREFAS")
    print("=" * 60)
    print("1. Adicionar nova tarefa")
    print("2. Listar todas as tarefas")
    print("3. Atualizar status de tarefa")
    print("4. Ver estatísticas")
    print("5. Adicionar tarefas de exemplo")
    print("6. Sair")
    print("=" * 60)

def add_sample_tasks():
    """Adiciona tarefas de exemplo para demonstração"""
    samples = [
        ("Estudar Docker Volumes", "Aprender sobre persistência de dados"),
        ("Configurar PostgreSQL", "Configurar banco de dados com volumes"),
        ("Documentar projeto", "Escrever README completo"),
        ("Testar persistência", "Verificar se dados persistem após restart")
    ]
    
    logging.info("Adicionando tarefas de exemplo...")
    for title, desc in samples:
        add_task(title, desc)
    
    logging.info(f"✓ {len(samples)} tarefas de exemplo adicionadas!")

def main():
    """Função principal da aplicação"""
    logging.info("=" * 60)
    logging.info("Iniciando aplicação de gerenciamento de tarefas")
    logging.info("=" * 60)
    
    # Aguarda o banco estar pronto
    if not wait_for_db():
        logging.error("Encerrando aplicação - banco de dados indisponível")
        return
    
    # Inicializa o banco de dados
    initialize_database()
    
    # Menu interativo
    while True:
        show_menu()
        choice = input("\nEscolha uma opção: ").strip()
        
        try:
            if choice == '1':
                title = input("Título da tarefa: ").strip()
                description = input("Descrição (opcional): ").strip()
                if title:
                    add_task(title, description)
                else:
                    print("✗ Título não pode ser vazio!")
            
            elif choice == '2':
                tasks = list_tasks()
                if tasks:
                    print("\n" + "=" * 60)
                    print("LISTA DE TAREFAS")
                    print("=" * 60)
                    for task in tasks:
                        print(f"\nID: {task[0]}")
                        print(f"Título: {task[1]}")
                        print(f"Descrição: {task[2]}")
                        print(f"Status: {task[3]}")
                        print(f"Criada em: {task[4]}")
                        print(f"Atualizada em: {task[5]}")
                        print("-" * 60)
                else:
                    print("\nNenhuma tarefa encontrada.")
            
            elif choice == '3':
                task_id = input("ID da tarefa: ").strip()
                print("\nStatus disponíveis: pending, in_progress, completed, cancelled")
                new_status = input("Novo status: ").strip()
                if task_id.isdigit() and new_status:
                    update_task_status(int(task_id), new_status)
                else:
                    print("✗ Entrada inválida!")
            
            elif choice == '4':
                stats = get_statistics()
                print("\n" + "=" * 60)
                print("ESTATÍSTICAS DO BANCO DE DADOS")
                print("=" * 60)
                print(f"Total de tarefas: {stats['total_tasks']}")
                print(f"Total de operações registradas: {stats['total_operations']}")
                print("\nTarefas por status:")
                for status, count in stats['status_counts'].items():
                    print(f"  - {status}: {count}")
            
            elif choice == '5':
                add_sample_tasks()
            
            elif choice == '6':
                print("\nEncerrando aplicação...")
                break
            
            else:
                print("\n✗ Opção inválida!")
        
        except Exception as e:
            logging.error(f"Erro: {e}")
            print(f"\n✗ Erro: {e}")

if __name__ == "__main__":
    main()
