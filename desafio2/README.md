# Desafio 2 — Volumes e Persistência

## 📋 Descrição da Solução

Este desafio demonstra o uso de **Docker Volumes** para persistência de dados. A solução consiste em:

1. **Container PostgreSQL**: Banco de dados com volume montado
2. **Aplicação de Tarefas**: Interface interativa para gerenciar tarefas
3. **Leitor de Dados**: Container separado que lê dados persistidos

O objetivo principal é demonstrar que **dados armazenados em volumes Docker persistem mesmo após a remoção dos containers**.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│              Rede: desafio2-network                     │
│                                                         │
│  ┌──────────────────┐         ┌────────────────────┐   │
│  │   postgres-db    │◄────────┤   tasks-app        │   │
│  │                  │         │                    │   │
│  │  PostgreSQL 15   │         │  Python App        │   │
│  │  Port: 5432      │         │  (Gerencia Tarefas)│   │
│  └────────┬─────────┘         └────────────────────┘   │
│           │                                             │
│           │ Volume Mount                                │
└───────────┼─────────────────────────────────────────────┘
            │
            ▼
   ┌─────────────────────┐
   │  Docker Volume      │
   │  desafio2-postgres- │
   │  data               │
   │                     │
   │  /var/lib/          │
   │  postgresql/data    │
   └─────────────────────┘
            │
            │ Pode ser lido por
            ▼
   ┌─────────────────────┐
   │   data-reader       │
   │   (Lê dados         │
   │   persistidos)      │
   └─────────────────────┘
```

### Componentes:

#### 1. **PostgreSQL Container**
- **Imagem**: postgres:15-alpine (imagem leve)
- **Volume montado**: `/var/lib/postgresql/data`
- **Database**: tasksdb
- **Tabelas**:
  - `tasks`: armazena tarefas com título, descrição, status
  - `operation_logs`: registra todas as operações realizadas

#### 2. **Aplicação de Tarefas (Python)**
- Interface interativa via terminal
- Operações CRUD completas
- Logging detalhado de operações
- Conexão via psycopg2

#### 3. **Leitor de Dados**
- Container separado que demonstra persistência
- Lê dados mesmo após remover container original
- Exibe estatísticas e histórico

#### 4. **Docker Volume**
- Nome: `desafio2-postgres-data`
- Tipo: Local driver
- Persistência: Dados sobrevivem à remoção de containers
- Localização: Gerenciada pelo Docker

## 🔧 Decisões Técnicas

### Por que PostgreSQL?
- **Banco relacional robusto**: Perfeito para demonstrar persistência
- **Imagem Alpine**: Versão leve (~80MB vs ~150MB da versão normal)
- **Amplamente usado**: Relevante para cenários reais
- **Excelente suporte Python**: Driver psycopg2 maduro e estável

### Por que Volumes ao invés de Bind Mounts?
- **Gerenciados pelo Docker**: Não dependem de estrutura de diretórios do host
- **Portabilidade**: Funcionam igualmente em todos os sistemas operacionais
- **Performance**: Melhor desempenho em Mac e Windows
- **Facilidade**: Comandos `docker volume` facilitam gerenciamento

### Estrutura de Dados
```sql
-- Tabela de Tarefas
tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Tabela de Logs
operation_logs (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(50),
    details TEXT,
    timestamp TIMESTAMP
)
```

### Retry Logic
- Cliente aguarda até 30 tentativas (60 segundos) para DB estar pronto
- Essencial para inicialização confiável
- Evita race conditions

## 📊 Funcionamento Detalhado

### 1. **Criação do Volume**
```bash
docker volume create desafio2-postgres-data
```
- Cria um volume gerenciado pelo Docker
- Armazena dados em local específico do sistema
- Mac/Linux: `/var/lib/docker/volumes/`
- Windows/Mac (Docker Desktop): VM interna do Docker

### 2. **Montagem do Volume no Container**
```bash
docker run -d \
    --name postgres-db \
    -v desafio2-postgres-data:/var/lib/postgresql/data \
    postgres:15-alpine
```
- `-v volume:path`: Monta o volume no caminho especificado
- `/var/lib/postgresql/data`: Diretório padrão de dados do PostgreSQL
- Qualquer dado escrito neste caminho vai para o volume

### 3. **Persistência em Ação**
1. **Aplicação escreve dados** → PostgreSQL salva em `/var/lib/postgresql/data`
2. **Docker persiste dados** → Volume armazena fora do container
3. **Container é removido** → Dados permanecem no volume
4. **Novo container é criado** → Mesmos dados disponíveis imediatamente

### 4. **Ciclo de Vida dos Dados**
```
Aplicação → PostgreSQL → Container FS → Docker Volume → Host FS
   ↑                                                        │
   └────────────────────────────────────────────────────────┘
          (Dados persistem independente do container)
```

## 🚀 Instruções de Execução

### Pré-requisitos
- Docker instalado
- Bash shell
- ~500MB de espaço em disco

### Passo 1: Dar permissões aos scripts
```bash
chmod +x run.sh stop.sh test-persistence.sh
```

### Passo 2: Executar a aplicação
```bash
./run.sh
```

O script irá:
1. Criar o volume Docker
2. Criar a rede
3. Iniciar PostgreSQL com volume montado
4. Construir e iniciar a aplicação
5. Abrir interface interativa

### Passo 3: Usar a aplicação
Menu interativo:
```
1. Adicionar nova tarefa
2. Listar todas as tarefas
3. Atualizar status de tarefa
4. Ver estatísticas
5. Adicionar tarefas de exemplo
6. Sair
```

**Exemplo de uso:**
1. Escolha opção `5` para adicionar tarefas de exemplo
2. Escolha opção `2` para ver as tarefas criadas
3. Escolha opção `4` para ver estatísticas
4. Escolha opção `6` para sair

### Passo 4: Demonstrar persistência
```bash
# Parar e remover containers (mas manter volume)
./stop.sh

# Testar que os dados persistiram
./test-persistence.sh
```

O script `test-persistence.sh` irá:
1. Verificar que o volume ainda existe
2. Iniciar um novo container PostgreSQL com o mesmo volume
3. Usar um container leitor para exibir os dados
4. **Demonstrar que os dados permaneceram intactos!**

### Passo 5: Verificar o volume
```bash
# Listar volumes
docker volume ls

# Inspecionar o volume
docker volume inspect desafio2-postgres-data

# Ver tamanho do volume
docker system df -v | grep desafio2-postgres-data
```

### Passo 6: Testar persistência manualmente
```bash
# 1. Criar alguns dados com run.sh
./run.sh
# (Adicione algumas tarefas e saia)

# 2. Remover TODOS os containers
docker stop postgres-db tasks-app
docker rm postgres-db tasks-app

# 3. Iniciar apenas o PostgreSQL novamente
docker run -d \
    --name postgres-db \
    --network desafio2-network \
    -v desafio2-postgres-data:/var/lib/postgresql/data \
    postgres:15-alpine

# 4. Verificar dados persistidos
./test-persistence.sh
```

✅ **Resultado esperado**: Todos os dados estarão presentes!

## 📝 Exemplo de Saída

### Executando a aplicação:
```
=============================== =============================
SISTEMA DE GERENCIAMENTO DE TAREFAS
==========================================================
1. Adicionar nova tarefa
2. Listar todas as tarefas
3. Atualizar status de tarefa
4. Ver estatísticas
5. Adicionar tarefas de exemplo
6. Sair
==========================================================

Escolha uma opção: 5

2025-11-18 11:00:00 - INFO - Adicionando tarefas de exemplo...
2025-11-18 11:00:00 - INFO - ✓ Tarefa 'Estudar Docker Volumes' adicionada com ID 1
2025-11-18 11:00:00 - INFO - ✓ Tarefa 'Configurar PostgreSQL' adicionada com ID 2
...
```

### Testando persistência:
```
============================================================
Demonstração de Persistência - Desafio 2
============================================================

📊 INFORMAÇÕES DO BANCO DE DADOS
Tamanho: 8.12 MB
Tabelas: tasks, operation_logs

==========================================================
📝 TAREFAS PERSISTIDAS
==========================================================

┌─ Tarefa ID: 1
│  Título: Estudar Docker Volumes
│  Descrição: Aprender sobre persistência de dados
│  Status: pending
│  Criada em: 2025-11-18 11:00:00
└─ Atualizada em: 2025-11-18 11:00:00

✓ Total de tarefas encontradas: 4
```

## 🧪 Testes de Validação

### Teste 1: Criação e Persistência Básica
```bash
# Execute e adicione dados
./run.sh
# (Adicione tarefas e saia)

# Verifique que volume existe
docker volume inspect desafio2-postgres-data

# Leia os dados
./test-persistence.sh
```
✅ **Esperado**: Dados aparecem no leitor

### Teste 2: Remoção e Recriação de Container
```bash
# Remova tudo exceto volume
docker stop postgres-db && docker rm postgres-db
docker network create desafio2-network

# Recrie container com mesmo volume
docker run -d \
    --name postgres-db \
    --network desafio2-network \
    -v desafio2-postgres-data:/var/lib/postgresql/data \
    postgres:15-alpine

# Leia dados
./test-persistence.sh
```
✅ **Esperado**: Dados intactos

### Teste 3: Múltiplos Containers Lendo Mesmo Volume
```bash
# Com PostgreSQL rodando, execute leitor múltiplas vezes
./test-persistence.sh
./test-persistence.sh
```
✅ **Esperado**: Mesmos dados em todas as execuções

### Teste 4: Verificação de Tamanho
```bash
# Antes de adicionar dados
docker volume inspect desafio2-postgres-data

# Adicione muitos dados via aplicação

# Depois
docker volume inspect desafio2-postgres-data
docker system df -v
```
✅ **Esperado**: Tamanho do volume aumenta

## 🎯 Pontos de Avaliação

### ✅ Uso correto de volumes (5 pts)
- Volume criado com `docker volume create`
- Montado corretamente no caminho PostgreSQL
- Dados efetivamente armazenados no volume

### ✅ Persistência comprovada após recriação (5 pts)
- Containers removidos completamente
- Novos containers criados
- Dados acessíveis e íntegros
- Script `test-persistence.sh` demonstra claramente

### ✅ README com explicação e prints/resultados (5 pts)
- Arquitetura documentada
- Fluxo de persistência explicado
- Exemplos de saída incluídos
- Instruções detalhadas de teste

### ✅ Clareza e organização do código (5 pts)
- Código Python bem estruturado
- Comentários explicativos
- Scripts shell organizados
- Separação clara de responsabilidades

## 🔍 Detalhes de Implementação

### Esquema do Banco de Dados
```sql
-- Criação automática na primeira execução
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE operation_logs (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(50) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Configuração PostgreSQL
```bash
POSTGRES_DB=tasksdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
VOLUME_MOUNT=/var/lib/postgresql/data
```

### Conexão Python
```python
DB_CONFIG = {
    'host': 'postgres-db',  # Nome do container
    'database': 'tasksdb',
    'user': 'postgres',
    'password': 'postgres',
    'port': '5432'
}
```

## 🛠️ Troubleshooting

### Problema: "Volume already exists"
```bash
# Verificar volume existente
docker volume inspect desafio2-postgres-data

# Se quiser recomeçar do zero
docker volume rm desafio2-postgres-data
```

### Problema: "Connection refused" ao conectar
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres-db

# Ver logs do PostgreSQL
docker logs postgres-db

# PostgreSQL pode demorar alguns segundos para iniciar
# Aguarde e tente novamente
```

### Problema: Dados não persistem
```bash
# Verificar se volume está montado corretamente
docker inspect postgres-db | grep -A 10 Mounts

# Deve mostrar:
# "Source": "/var/lib/docker/volumes/desafio2-postgres-data/_data"
# "Destination": "/var/lib/postgresql/data"
```

### Problema: "Permission denied" no volume
```bash
# Em alguns sistemas, pode ser necessário
# dar permissões ao volume
docker run --rm -v desafio2-postgres-data:/data alpine chown -R 999:999 /data
```

## 📚 Conceitos Demonstrados

1. **Docker Volumes**: Persistência de dados independente de containers
2. **Volume Lifecycle**: Criação, uso, inspeção e remoção
3. **Data Persistence**: Dados sobrevivem à remoção de containers
4. **PostgreSQL**: Configuração e uso em containers
5. **Python Database Access**: psycopg2 e best practices
6. **Container Networking**: Comunicação entre app e banco
7. **Error Handling**: Retry logic e tratamento de exceções
8. **Logging**: Auditoria de operações de banco de dados

## 🎓 Aprendizados

### Volumes vs Bind Mounts
- **Volumes**: Gerenciados pelo Docker, portáveis, recomendados
- **Bind Mounts**: Dependentes de estrutura do host, menos portáveis

### Quando usar Volumes?
- ✅ Bancos de dados (PostgreSQL, MySQL, MongoDB)
- ✅ Dados que precisam persistir
- ✅ Compartilhamento de dados entre containers
- ✅ Backup e restore de dados

### Localização dos Volumes
- **Linux**: `/var/lib/docker/volumes/`
- **Mac/Windows**: Dentro da VM do Docker Desktop
- **Acesso**: `docker volume inspect` mostra localização

### Backup de Volumes
```bash
# Backup
docker run --rm \
    -v desafio2-postgres-data:/data \
    -v $(pwd):/backup \
    alpine tar czf /backup/backup.tar.gz /data

# Restore
docker run --rm \
    -v desafio2-postgres-data:/data \
    -v $(pwd):/backup \
    alpine tar xzf /backup/backup.tar.gz -C /
```

---

**Autor**: Arthur Campos  
**Data**: Novembro 2025  
**Tecnologias**: Docker, PostgreSQL, Python, psycopg2
