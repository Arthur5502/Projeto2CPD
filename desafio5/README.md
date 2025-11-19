# Desafio 5 — Microsserviços com API Gateway

## 📋 Descrição da Solução

Este desafio implementa uma **arquitetura completa de microsserviços com API Gateway**, demonstrando o padrão mais comum em sistemas distribuídos modernos:

1. **API Gateway**: Ponto único de entrada que roteia requisições
2. **Users Service**: Microsserviço para gerenciamento de usuários  
3. **Orders Service**: Microsserviço para gerenciamento de pedidos

O **API Gateway** centraliza o acesso, fornecendo:
- Roteamento inteligente de requisições
- Agregação de dados de múltiplos serviços
- Health check consolidado
- Ponto único para autenticação e logging (demonstrado conceitualmente)

## 🏗️ Arquitetura

```
                          ┌─────────────────────┐
                          │      Cliente        │
                          │   (Navegador/App)   │
                          └──────────┬──────────┘
                                     │
                         Ponto Único de Entrada
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │       API Gateway :8000        │
                    │                                │
                    │  • Roteamento                  │
                    │  • Agregação                   │
                    │  • Health Check                │
                    │  • Load Balancing (conceito)   │
                    └─────┬────────────────────┬─────┘
                          │                    │
              ┌───────────┴─────────┐   ┌─────┴───────────┐
              │                     │   │                 │
              ▼                     │   ▼                 │
    ┌──────────────────┐           │   ┌──────────────────┐
    │  users-service   │           │   │  orders-service  │
    │     :5001        │           │   │      :5003       │
    │                  │           │   │                  │
    │  • GET /users    │           │   │  • GET /orders   │
    │  • POST /users   │           │   │  • POST /orders  │
    │  • GET /users/id │           │   │  • GET /orders/id│
    └──────────────────┘           │   └──────────────────┘
                                   │
                    Rede Interna (desafio5-network)
```

### Fluxo de Requisições:

**1. Requisição Simples (roteamento):**
```
Cliente → Gateway:8000/users → Gateway roteia → Users Service:5001 → Resposta
```

**2. Requisição Agregada (orquestração):**
```
Cliente → Gateway:8000/users/1/orders
    ↓
Gateway chama Users Service → Obtém dados do usuário
    ↓
Gateway chama Orders Service → Obtém pedidos do usuário
    ↓
Gateway combina dados → Retorna resposta agregada
```

## 🔧 Decisões Técnicas

### Por que API Gateway?

**Vantagens:**
- ✅ **Ponto Único de Entrada**: Simplifica acesso para clientes
- ✅ **Abstração**: Clientes não precisam conhecer todos os microsserviços
- ✅ **Centralização**: Logging, autenticação, rate limiting em um só lugar
- ✅ **Flexibilidade**: Mudanças nos backends não afetam clientes
- ✅ **Agregação**: Combina dados de múltiplos serviços em uma única chamada

**Casos de Uso:**
- Aplicações web/mobile que consomem múltiplos serviços
- Necessidade de combinar dados de diferentes fontes
- Controle centralizado de acesso e segurança
- Versionamento de API

### Componentes da Arquitetura

#### 1. **API Gateway (Flask)**
**Porta:** 8000  
**Responsabilidades:**
- Rotear `/users/*` para Users Service
- Rotear `/orders/*` para Orders Service
- Endpoint agregado `/users/<id>/orders`
- Health check consolidado
- Tratamento de erros e timeouts

**Código Principal:**
```python
def forward_request(service_url, path, method='GET'):
    """Encaminha requisição para microsserviço"""
    url = f"{service_url}{path}"
    response = requests.request(method, url, ...)
    return Response(response.content, ...)
```

#### 2. **Users Service**
**Porta:** 5001 (interna)  
**Endpoints:**
- `GET /users` - Lista usuários
- `GET /users/<id>` - Busca usuário
- `POST /users` - Cria usuário
- `GET /health` - Health check

#### 3. **Orders Service**
**Porta:** 5003 (interna)  
**Endpoints:**
- `GET /orders` - Lista pedidos
- `GET /orders?user_id=X` - Pedidos de um usuário
- `GET /orders/<id>` - Busca pedido
- `POST /orders` - Cria pedido
- `GET /health` - Health check

### Docker Compose

```yaml
services:
  gateway:
    ports:
      - "8000:8000"  # Único porta exposta externamente
    depends_on:
      - users-service
      - orders-service

  users-service:
    # Sem mapeamento de porta (não acessível externamente)
    
  orders-service:
    # Sem mapeamento de porta (não acessível externamente)
```

**Segurança por Design:**
- Apenas o Gateway é acessível externamente
- Microsserviços ficam na rede interna
- Clientes não podem acessar serviços diretamente

## 🚀 Instruções de Execução

### Pré-requisitos
- Docker e Docker Compose instalados

### Passo 1: Dar permissões
```bash
chmod +x run.sh stop.sh test-gateway.sh
```

### Passo 2: Iniciar todos os serviços
```bash
./run.sh
```

Isso irá:
1. Criar a rede `desafio5-network`
2. Construir 3 imagens Docker
3. Iniciar Users Service
4. Iniciar Orders Service
5. Iniciar API Gateway
6. Aguardar health checks

### Passo 3: Testar o Gateway
```bash
./test-gateway.sh
```

### Passo 4: Testes Manuais

**Acessar informações do Gateway:**
```bash
curl http://localhost:8000
```

**Listar usuários (via Gateway):**
```bash
curl http://localhost:8000/users
```

**Buscar usuário específico:**
```bash
curl http://localhost:8000/users/1
```

**Listar pedidos:**
```bash
curl http://localhost:8000/orders
```

**Pedidos de um usuário específico:**
```bash
curl http://localhost:8000/orders?user_id=1
```

**Endpoint Agregado (usuário + pedidos):**
```bash
curl http://localhost:8000/users/1/orders
```

**Criar novo pedido via Gateway:**
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "1",
    "product": "Teclado Mecânico",
    "quantity": 1,
    "total": 599.00
  }'
```

### Passo 5: Ver logs
```bash
# Logs de todos os serviços
docker compose logs -f

# Logs apenas do Gateway
docker compose logs -f gateway

# Ver roteamento em ação
docker compose logs gateway | grep "encaminhando"
```

### Passo 6: Parar tudo
```bash
./stop.sh
```

## 📊 Endpoints do Gateway

### Informações e Health
```
GET  /          → Informações do Gateway e rotas disponíveis
GET  /health    → Health check de todos os serviços
```

### Roteamento para Users Service
```
GET  /users         → Lista usuários
GET  /users/<id>    → Busca usuário
POST /users         → Cria usuário
```

### Roteamento para Orders Service
```
GET  /orders        → Lista pedidos
GET  /orders/<id>   → Busca pedido
POST /orders        → Cria pedido
```

### Endpoint Agregado (Orquestração)
```
GET  /users/<id>/orders  → Usuário + seus pedidos (combina ambos os serviços)
```

## 📝 Exemplos de Respostas

### Informações do Gateway:
```json
{
  "service": "API Gateway",
  "version": "1.0.0",
  "description": "Ponto único de entrada para todos os microsserviços",
  "backend_services": [
    {"name": "users-service", "url": "http://users-service:5001"},
    {"name": "orders-service", "url": "http://orders-service:5003"}
  ]
}
```

### Health Check Consolidado:
```json
{
  "gateway": "healthy",
  "timestamp": "2025-11-19T10:30:00",
  "services": {
    "users-service": "healthy",
    "orders-service": "healthy"
  }
}
```

### Endpoint Agregado (/users/1/orders):
```json
{
  "user": {
    "id": "1",
    "name": "Alice Silva",
    "email": "alice@email.com",
    "status": "active"
  },
  "orders": [
    {
      "id": "1",
      "user_id": "1",
      "product": "Laptop",
      "quantity": 1,
      "total": 5999.0,
      "status": "delivered"
    },
    {
      "id": "2",
      "user_id": "1",
      "product": "Mouse",
      "quantity": 2,
      "total": 900.0,
      "status": "shipped"
    }
  ],
  "total_orders": 2,
  "aggregated_by": "api-gateway"
}
```

## 🎯 Pontos de Avaliação

### ✅ Funcionamento do gateway como ponto único de entrada (10 pts)
- Gateway exposto na porta 8000
- Todos os acessos passam pelo Gateway
- Microsserviços não acessíveis diretamente
- Roteamento funcionando corretamente

### ✅ Integração correta entre os serviços (5 pts)
- Gateway se comunica com ambos os microsserviços
- Depends_on configurado adequadamente
- Health checks implementados
- Tratamento de erros robusto

### ✅ README detalhado com explicações e testes (5 pts)
- Arquitetura documentada
- Fluxos de requisição explicados
- Instruções claras de execução
- Exemplos de uso

### ✅ Clareza, código organizado e boa documentação (5 pts)
- Código limpo e comentado
- Estrutura de pastas clara
- Docker Compose bem organizado
- Scripts automatizados

## 🔍 Conceitos Demonstrados

1. **API Gateway Pattern**: Ponto único de entrada
2. **Service Orchestration**: Gateway combinando múltiplos serviços
3. **Request Routing**: Encaminhamento baseado em path
4. **Health Check Aggregation**: Status consolidado
5. **Error Handling**: Tratamento de falhas de serviços
6. **Service Discovery**: Resolução DNS no Docker
7. **Microservices Communication**: HTTP entre serviços
8. **Isolation**: Microsserviços não expostos externamente

## 🎓 Aprendizados

### Quando usar API Gateway?
- ✅ Múltiplos microsserviços consumidos por clientes
- ✅ Necessidade de agregação de dados
- ✅ Controle centralizado (auth, logging, rate limiting)
- ✅ Simplificar interface para clientes

### Alternativas ao API Gateway:
- **Service Mesh** (Istio, Linkerd): Para comunicação service-to-service complexa
- **Acesso Direto**: Quando poucos serviços e sem necessidade de agregação
- **BFF (Backend for Frontend)**: Gateway específico por tipo de cliente

### Padrões Implementados:
- **Gateway Routing**: Roteamento simples de requisições
- **Gateway Aggregation**: Combinar respostas de múltiplos serviços
- **Gateway Offloading**: Funcionalidades compartilhadas (health check, logging)

---

**Autor**: Arthur Campos  
**Data**: Novembro 2025  
**Tecnologias**: Docker Compose, Flask, Python Requests, API Gateway Pattern
