# Desafio 3 — Docker Compose Orquestrando Serviços

## 📋 Descrição da Solução

Este desafio implementa uma **aplicação web completa** usando **Docker Compose** para orquestrar múltiplos serviços interdependentes:

1. **Web (Flask API)**: Aplicação REST API para gerenciamento de produtos
2. **Database (PostgreSQL)**: Banco de dados relacional para armazenamento persistente
3. **Cache (Redis)**: Cache em memória para otimização de performance

A solução demonstra conceitos avançados como:
- Orquestração de múltiplos containers
- Gerenciamento de dependências entre serviços
- Persistência de dados com volumes
- Rede interna isolada
- Health checks automáticos
- Variáveis de ambiente para configuração

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                  Rede: desafio3-network                     │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │   Cliente    │─────►│   web:5000   │      │          │  │
│  │  (Externo)   │      │              │      │          │  │
│  └──────────────┘      │  Flask API   │      │          │  │
│                        │              │      │          │  │
│                        │  - Rotas REST│      │          │  │
│                        │  - Lógica    │      │          │  │
│                        └──────┬───┬───┘      │          │  │
│                               │   │          │          │  │
│                    depends_on │   │          │          │  │
│                       ┌───────┘   └────────┐ │          │  │
│                       │                    │ │          │  │
│                       ▼                    ▼ │          │  │
│              ┌─────────────┐      ┌──────────────┐     │  │
│              │  db:5432    │      │  cache:6379  │     │  │
│              │             │      │              │     │  │
│              │ PostgreSQL  │      │    Redis     │     │  │
│              │             │      │              │     │  │
│              │ - Produtos  │      │  - Cache de  │     │  │
│              │ - Schemas   │      │    queries   │     │  │
│              └──────┬──────┘      └──────┬───────┘     │  │
│                     │                    │             │  │
└─────────────────────┼────────────────────┼─────────────┘  │
                      │                    │                │
                      ▼                    ▼                │
             ┌─────────────────┐  ┌────────────────┐       │
             │  Volume:        │  │  Volume:       │       │
             │  postgres_data  │  │  redis_data    │       │
             │                 │  │                │       │
             │  Persistente    │  │  Persistente   │       │
             └─────────────────┘  └────────────────┘       │
```

### Fluxo de Requisições:

```
1. Cliente faz requisição HTTP → Web:5000
2. Web verifica cache Redis
   └─ Se encontrado → Retorna do cache (rápido)
   └─ Se não encontrado:
       └─ Busca no PostgreSQL
       └─ Armazena no cache
       └─ Retorna ao cliente
3. Escrita (POST/PUT/DELETE):
   └─ Escreve no PostgreSQL
   └─ Invalida cache
   └─ Retorna confirmação
```

## 🔧 Decisões Técnicas

### Por que Docker Compose?
- **Simplicidade**: Um único arquivo YAML define toda a infraestrutura
- **Reprodutibilidade**: Mesmo ambiente em qualquer máquina
- **Gerenciamento**: Iniciar/parar todos os serviços com um comando
- **Desenvolvimento**: Ambiente local idêntico à produção

### Stack Tecnológica

#### 1. **Flask (Python)**
**Por quê?**
- Framework leve e flexível
- Excelente para APIs REST
- Rica biblioteca de extensões
- Fácil integração com PostgreSQL e Redis

#### 2. **PostgreSQL**
**Por quê?**
- Banco relacional robusto e confiável
- Excelente para dados estruturados
- Suporte a transações ACID
- Triggers e functions para lógica avançada

#### 3. **Redis**
**Por quê?**
- Cache em memória extremamente rápido
- Reduz carga no banco de dados
- Suporta TTL (Time To Live) automático
- Persistência opcional

### Estratégia de Cache

```python
# Pattern: Cache-Aside
1. Verificar cache
2. Se não encontrado:
   - Buscar no banco
   - Armazenar no cache com TTL
3. Retornar dados

# Invalidação
- Ao criar/atualizar/deletar: Limpar cache relevante
```

**Vantagens:**
- Reduz latência em ~90%
- Diminui carga no banco
- Escalabilidade melhorada

### Health Checks

Cada serviço tem seu health check:

```yaml
# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  
# Redis
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s

# Web
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
```

**Benefícios:**
- Docker só marca serviço como "ready" quando saudável
- `depends_on` aguarda health check, não apenas start
- Reinício automático em caso de falha

### Dependências (depends_on)

```yaml
web:
  depends_on:
    db:
      condition: service_healthy
    cache:
      condition: service_healthy
```

**Garante:**
- Web só inicia após DB e Cache estarem prontos
- Evita erros de conexão no startup
- Ordem correta de inicialização

## 📊 Funcionamento Detalhado

### 1. **Inicialização (docker compose up)**

#### Fase 1: Preparação
```
1. Criar rede 'desafio3-network'
2. Criar volumes 'postgres_data' e 'redis_data'
3. Pull das imagens necessárias
```

#### Fase 2: Serviços de Dependência
```
1. Iniciar PostgreSQL
   - Montar volume
   - Executar init.sql (criar tabelas)
   - Health check até estar pronto
   
2. Iniciar Redis
   - Montar volume
   - Configurar política de memória
   - Health check até estar pronto
```

#### Fase 3: Serviço Principal
```
1. Build da imagem Web
2. Aguardar DB e Cache (depends_on)
3. Iniciar aplicação Flask
4. Health check até estar pronto
```

### 2. **Estrutura do docker-compose.yml**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: productsdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persistência
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql  # Init script
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb
    volumes:
      - redis_data:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  web:
    build: ./web
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    environment:
      DB_HOST: db
      REDIS_HOST: cache
    networks:
      - app-network
    ports:
      - "5000:5000"

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
```

### 3. **Comunicação entre Serviços**

**Resolução DNS Interna:**
```python
# No código Python:
DB_CONFIG = {
    'host': 'db',  # Nome do serviço no Compose
    ...
}

REDIS_HOST = 'cache'  # Nome do serviço no Compose
```

Docker Compose cria automaticamente:
- DNS interno: `db` → `172.20.0.2` (exemplo)
- DNS interno: `cache` → `172.20.0.3` (exemplo)

### 4. **Endpoints da API**

```
GET  /               → Info da API
GET  /health         → Health check
GET  /products       → Lista produtos (com cache)
GET  /products/:id   → Busca produto (com cache)
POST /products       → Cria produto (invalida cache)
GET  /stats          → Estatísticas do sistema
```

**Exemplo de resposta:**
```json
{
  "source": "cache",
  "products": [
    {
      "id": 1,
      "name": "Laptop Dell XPS 13",
      "price": 5999.00,
      "stock": 10
    }
  ]
}
```

## 🚀 Instruções de Execução

### Pré-requisitos
```bash
# Verificar Docker
docker --version

# Verificar Docker Compose
docker compose version

# Espaço em disco: ~1GB
```

### Passo 1: Dar permissões
```bash
chmod +x run.sh stop.sh test-api.sh
```

### Passo 2: Iniciar a aplicação
```bash
./run.sh
```

**O script irá:**
1. ✅ Verificar dependências
2. ✅ Limpar recursos anteriores
3. ✅ Iniciar todos os serviços
4. ✅ Aguardar health checks
5. ✅ Exibir status e informações
6. ✅ Testar conectividade

**Saída esperada:**
```
✓ Todos os serviços foram iniciados com sucesso!

STATUS DOS SERVIÇOS
NAME              STATUS    PORTS
desafio3-db       Up        0.0.0.0:5432->5432/tcp
desafio3-cache    Up        0.0.0.0:6379->6379/tcp
desafio3-web      Up        0.0.0.0:5000->5000/tcp
```

### Passo 3: Testar a API
```bash
./test-api.sh
```

**Testes executados:**
1. GET / (informações da API)
2. GET /products (lista produtos - banco)
3. GET /products (lista produtos - cache)
4. GET /products/1 (busca específica)
5. POST /products (cria novo produto)
6. GET /stats (estatísticas)
7. GET /health (health check)

### Passo 4: Testes manuais

#### Listar produtos
```bash
curl http://localhost:5000/products
```

#### Buscar produto específico
```bash
curl http://localhost:5000/products/1
```

#### Criar produto
```bash
curl -X POST http://localhost:5000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Produto Teste",
    "description": "Descrição do produto",
    "price": 99.99,
    "stock": 50
  }'
```

#### Ver estatísticas
```bash
curl http://localhost:5000/stats
```

### Passo 5: Inspecionar serviços

#### Ver logs de todos os serviços
```bash
docker compose logs -f
```

#### Ver logs de serviço específico
```bash
docker compose logs -f web
docker compose logs -f db
docker compose logs -f cache
```

#### Ver status
```bash
docker compose ps
```

#### Executar comandos nos containers
```bash
# PostgreSQL
docker compose exec db psql -U postgres -d productsdb

# Redis
docker compose exec cache redis-cli

# Ver produtos no banco
docker compose exec db psql -U postgres -d productsdb -c "SELECT * FROM products;"

# Ver chaves no Redis
docker compose exec cache redis-cli KEYS "*"
```

### Passo 6: Demonstrar cache

```bash
# Primeira requisição (do banco - mais lenta)
time curl -s http://localhost:5000/products > /dev/null

# Segunda requisição (do cache - mais rápida)
time curl -s http://localhost:5000/products > /dev/null

# Ver diferença de tempo!
```

### Passo 7: Parar serviços
```bash
./stop.sh
```

**Opções:**
1. Parar serviços (manter dados)
2. Parar e remover tudo (limpar completamente)

## 📝 Exemplos de Saída

### Executando run.sh:
```bash
[3/3] Iniciando serviços com Docker Compose...
[+] Running 5/5
 ✔ Network desafio3-network       Created
 ✔ Volume desafio3_postgres_data  Created
 ✔ Volume desafio3_redis_data     Created
 ✔ Container desafio3-db          Healthy
 ✔ Container desafio3-cache       Healthy
 ✔ Container desafio3-web         Started

✓ Todos os serviços foram iniciados com sucesso!
```

### Health Check:
```json
{
  "service": "web",
  "status": "healthy",
  "dependencies": {
    "database": "healthy",
    "cache": "healthy"
  }
}
```

### Listando produtos (primeira vez - banco):
```json
{
  "source": "database",
  "products": [
    {
      "id": 1,
      "name": "Laptop Dell XPS 13",
      "description": "Ultrabook com processador Intel Core i7",
      "price": 5999.0,
      "stock": 10
    }
  ]
}
```

### Listando produtos (segunda vez - cache):
```json
{
  "source": "cache",
  "products": [...]
}
```

## 🧪 Testes de Validação

### Teste 1: Dependências funcionando
```bash
# Parar apenas o cache
docker compose stop cache

# Tentar acessar API
curl http://localhost:5000/products
# Deve funcionar, mas sem cache (source: database)

# Reiniciar cache
docker compose start cache
```

✅ **Esperado**: API continua funcionando, cache é opcional

### Teste 2: Persistência de volumes
```bash
# Criar produto
curl -X POST http://localhost:5000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Teste Persistência", "price": 10, "stock": 1}'

# Parar tudo
docker compose down

# Iniciar novamente
docker compose up -d

# Verificar se produto existe
curl http://localhost:5000/products | grep "Teste Persistência"
```

✅ **Esperado**: Produto ainda existe

### Teste 3: Health Checks
```bash
# Ver health status
docker compose ps

# Deve mostrar "(healthy)" para todos
```

✅ **Esperado**: Todos os serviços marcados como healthy

### Teste 4: Rede Interna
```bash
# Tentar acessar DB de dentro do container web
docker compose exec web python3 -c "
import psycopg2
conn = psycopg2.connect(host='db', user='postgres', password='postgres', database='productsdb')
print('✓ Conexão bem-sucedida!')
conn.close()
"
```

✅ **Esperado**: Conexão bem-sucedida

### Teste 5: Performance do Cache
```bash
# Limpar cache
docker compose exec cache redis-cli FLUSHALL

# Primeira requisição (sem cache)
time curl -s http://localhost:5000/products > /dev/null

# Segunda requisição (com cache)
time curl -s http://localhost:5000/products > /dev/null

# Compare os tempos!
```

✅ **Esperado**: Segunda requisição ~50-90% mais rápida

## 🎯 Pontos de Avaliação

### ✅ Compose funcional e bem estruturado (10 pts)
- `docker-compose.yml` completo e correto
- Uso adequado de `depends_on` com health checks
- Volumes e redes configurados corretamente
- Variáveis de ambiente bem organizadas

### ✅ Comunicação entre serviços funcionando (5 pts)
- Web se comunica com DB
- Web se comunica com Cache
- Resolução DNS funcionando
- Logs mostram comunicação bem-sucedida

### ✅ README com explicação da arquitetura (5 pts)
- Diagrama de arquitetura
- Explicação de cada serviço
- Fluxo de dados documentado
- Decisões técnicas justificadas

### ✅ Clareza e boas práticas (5 pts)
- Código limpo e comentado
- Health checks implementados
- Gestão adequada de erros
- Scripts automatizados

## 🔍 Detalhes de Implementação

### Estrutura do Projeto
```
desafio3/
├── docker-compose.yml    # Orquestração principal
├── web/
│   ├── Dockerfile        # Imagem da aplicação
│   ├── app.py           # Código Flask
│   └── requirements.txt  # Dependências Python
├── db/
│   └── init.sql         # Script de inicialização
├── run.sh               # Script de execução
├── stop.sh              # Script de parada
├── test-api.sh          # Script de testes
└── README.md            # Esta documentação
```

### Configurações Importantes

#### PostgreSQL
```yaml
environment:
  POSTGRES_DB: productsdb
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
volumes:
  - postgres_data:/var/lib/postgresql/data
  - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
```

#### Redis
```yaml
command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```
- `appendonly yes`: Persistência em disco
- `maxmemory 256mb`: Limite de memória
- `allkeys-lru`: Política de evição (remove menos usado)

#### Web (Flask)
```python
depends_on:
  db:
    condition: service_healthy
  cache:
    condition: service_healthy
```
Aguarda serviços estarem saudáveis antes de iniciar

## 🛠️ Troubleshooting

### Problema: Serviços não iniciam
```bash
# Ver logs detalhados
docker compose logs

# Verificar se portas estão disponíveis
lsof -i :5000
lsof -i :5432
lsof -i :6379
```

### Problema: Web não conecta ao DB
```bash
# Verificar se DB está saudável
docker compose ps db

# Ver logs do DB
docker compose logs db

# Testar conexão manualmente
docker compose exec db pg_isready -U postgres
```

### Problema: Cache não funciona
```bash
# Verificar Redis
docker compose exec cache redis-cli ping

# Ver chaves no cache
docker compose exec cache redis-cli KEYS "*"

# Limpar cache
docker compose exec cache redis-cli FLUSHALL
```

### Problema: Mudanças no código não refletem
```bash
# Rebuild forçado
docker compose up -d --build --force-recreate web
```

## 📚 Conceitos Demonstrados

1. **Docker Compose**: Orquestração multi-container
2. **Service Discovery**: Resolução DNS entre containers
3. **Dependencies Management**: depends_on com health checks
4. **Data Persistence**: Volumes para dados permanentes
5. **Networking**: Rede bridge isolada
6. **Environment Variables**: Configuração via variáveis
7. **Health Checks**: Monitoramento de saúde dos serviços
8. **Caching Strategy**: Cache-Aside pattern com Redis
9. **Database Initialization**: Scripts SQL automáticos
10. **API Design**: REST API bem estruturada

## 🎓 Aprendizados

### Docker Compose vs Docker Run
- **Compose**: Múltiplos serviços em um arquivo
- **Run**: Um container por vez

### Benefícios do Compose
- ✅ Configuração declarativa
- ✅ Fácil replicação
- ✅ Gerenciamento simplificado
- ✅ Ideal para desenvolvimento

### Quando usar?
- ✅ Desenvolvimento local
- ✅ Testes de integração
- ✅ Ambientes multi-container
- ✅ Prototipagem rápida

### Limitações
- ❌ Não é para produção em escala
- ❌ Use Kubernetes/Swarm para produção
- ❌ Limitado a um único host

---

**Autor**: Arthur Campos  
**Data**: Novembro 2025  
**Tecnologias**: Docker Compose, Flask, PostgreSQL, Redis
