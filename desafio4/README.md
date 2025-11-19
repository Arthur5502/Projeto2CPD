# Desafio 4 — Microsserviços Independentes

## 📋 Descrição da Solução

Este desafio implementa **dois microsserviços independentes** que se comunicam via **HTTP/REST**, demonstrando os conceitos fundamentais de arquitetura de microsserviços:

1. **Service A (Users Service)**: Microsserviço de gerenciamento de usuários
2. **Service B (Aggregator Service)**: Microsserviço que consome o Service A e agrega informações adicionais

A comunicação entre os serviços é feita através de requisições HTTP, sem necessidade de API Gateway nesta etapa, demonstrando comunicação direta entre microsserviços.

## 🏗️ Arquitetura

```
┌────────────────────────────────────────────────────────────────┐
│                  Rede: desafio4-network                        │
│                                                                │
│                                                                │
│  ┌──────────────┐                                             │
│  │   Cliente    │                                             │
│  │  (Externo)   │                                             │
│  └───┬──────┬───┘                                             │
│      │      │                                                 │
│      │      │ HTTP Requests                                   │
│      │      │                                                 │
│      ▼      ▼                                                 │
│  ┌──────────────────┐         ┌──────────────────┐           │
│  │   service-a      │◄────────┤   service-b      │           │
│  │   :5001          │  HTTP   │   :5002          │           │
│  │                  │ Request │                  │           │
│  │  Users Service   │         │  Aggregator      │           │
│  │                  │         │  Service         │           │
│  │  - CRUD Usuários │         │                  │           │
│  │  - Validações    │         │  - Consome A     │           │
│  │  - Estatísticas  │         │  - Agrega dados  │           │
│  │                  │         │  - Combina info  │           │
│  └──────────────────┘         └──────────────────┘           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Fluxo de Comunicação:

```
Cenário 1: Acesso direto ao Service A
Cliente → Service A (5001) → Resposta

Cenário 2: Acesso via Service B (com agregação)
Cliente → Service B (5002) → Service A (5001) → Service B → Cliente
                    ↓
             (Adiciona dados
              de atividade)
```

## 🔧 Decisões Técnicas

### Arquitetura de Microsserviços

**Por que dois serviços separados?**
- **Separação de Responsabilidades**: Cada serviço tem uma responsabilidade única
- **Independência**: Podem ser desenvolvidos, testados e implantados separadamente
- **Escalabilidade**: Cada serviço pode escalar independentemente
- **Manutenibilidade**: Mudanças em um não afetam diretamente o outro

### Service A (Users Service)

**Responsabilidades:**
- Gerenciar dados de usuários (CRUD completo)
- Validar dados de entrada
- Fornecer API REST para acesso aos usuários
- Estatísticas básicas

**Por que Flask?**
- Framework leve e ideal para APIs REST
- Fácil implementação de endpoints
- Excelente para microsserviços

**Estrutura de Dados:**
```python
{
    "id": "1",
    "name": "Alice Silva",
    "email": "alice.silva@email.com",
    "role": "developer",
    "active_since": "2023-01-15",
    "department": "Engineering",
    "status": "active"
}
```

### Service B (Aggregator Service)

**Responsabilidades:**
- Consumir dados do Service A via HTTP
- Agregar informações adicionais (atividades)
- Calcular métricas derivadas
- Fornecer endpoints de alto nível

**Padrão de Design: Aggregator Pattern**
- Coleta dados de múltiplas fontes
- Combina e enriquece informações
- Apresenta visão unificada

**Dados Adicionais:**
```python
{
    "last_login": "2025-11-18 14:30:00",
    "total_logins": 245,
    "projects": 8
}
```

### Comunicação HTTP

**Por que HTTP/REST?**
- **Padrão Universal**: Suportado por todas as linguagens
- **Stateless**: Cada requisição é independente
- **Cacheable**: Respostas podem ser cacheadas
- **Simples**: Fácil de debugar e testar

**Biblioteca requests (Python):**
```python
response = requests.get(f"{SERVICE_A_URL}/users/{user_id}")
```

**Vantagens:**
- Sintaxe simples e legível
- Tratamento robusto de erros
- Timeouts configuráveis
- Suporte completo a métodos HTTP

## 📊 Funcionamento Detalhado

### 1. Inicialização

```bash
./run.sh
```

**Passos executados:**
1. Criar rede Docker `desafio4-network`
2. Build da imagem do Service A
3. Build da imagem do Service B
4. Iniciar Service A na porta 5001
5. Iniciar Service B na porta 5002
6. Verificar conectividade

### 2. Service A - Endpoints

```
GET  /                → Informações do serviço
GET  /health          → Health check
GET  /users           → Lista todos os usuários
GET  /users?status=   → Filtra por status
GET  /users/<id>      → Busca usuário específico
POST /users           → Cria novo usuário
PUT  /users/<id>      → Atualiza usuário
DELETE /users/<id>    → Remove usuário
GET  /stats           → Estatísticas
```

**Exemplo - Criar usuário:**
```bash
curl -X POST http://localhost:5001/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@email.com",
    "role": "developer",
    "department": "Engineering"
  }'
```

### 3. Service B - Endpoints

```
GET /                      → Informações do serviço
GET /health                → Health check (verifica Service A também)
GET /users-info            → Usuários + atividades agregadas
GET /users-info/<id>       → Info completa de um usuário
GET /active-users          → Apenas usuários ativos com detalhes
GET /user-summary/<id>     → Resumo executivo
GET /stats                 → Estatísticas agregadas
```

**Exemplo - Usuários com informações agregadas:**
```bash
curl http://localhost:5002/users-info
```

**Resposta:**
```json
{
  "total": 5,
  "users": [
    {
      "id": "1",
      "name": "Alice Silva",
      "email": "alice.silva@email.com",
      "role": "developer",
      "department": "Engineering",
      "status": "active",
      "activity": {
        "last_login": "2025-11-18 14:30:00",
        "total_logins": 245,
        "projects": 8
      },
      "days_active": 673,
      "engagement_level": "high"
    }
  ],
  "aggregated_by": "service-b"
}
```

### 4. Comunicação Entre Serviços

**Service B chamando Service A:**

```python
# No código do Service B
SERVICE_A_URL = "http://service-a:5001"

def call_service_a(endpoint):
    url = f"{SERVICE_A_URL}{endpoint}"
    response = requests.get(url, timeout=10)
    return response.json()

# Uso
users_data = call_service_a('/users')
```

**Resolução DNS:**
- Docker resolve `service-a` para o IP do container
- Comunicação interna na rede `desafio4-network`
- Sem exposição de portas necessária (mas exposto para testes)

### 5. Agregação de Dados

**Processo:**
1. Service B recebe requisição do cliente
2. Service B faz requisição HTTP ao Service A
3. Service A retorna dados de usuários
4. Service B adiciona dados de atividade
5. Service B calcula métricas derivadas:
   - `days_active`: Dias desde cadastro
   - `engagement_level`: Nível de engajamento
   - `average_logins_per_day`: Média de logins
6. Service B retorna dados completos ao cliente

## 🚀 Instruções de Execução

### Pré-requisitos
- Docker instalado
- Curl ou navegador para testes
- Bash shell

### Passo 1: Dar permissões aos scripts
```bash
chmod +x run.sh stop.sh test-services.sh
```

### Passo 2: Executar os microsserviços
```bash
./run.sh
```

**Saída esperada:**
```
✓ Todos os microsserviços estão rodando!

NAME        STATUS    PORTS
service-a   Up        0.0.0.0:5001->5001/tcp
service-b   Up        0.0.0.0:5002->5002/tcp
```

### Passo 3: Testar comunicação
```bash
./test-services.sh
```

O script executa uma bateria completa de testes demonstrando:
- Funcionamento independente do Service A
- Comunicação entre Service B e Service A
- Agregação de dados
- Diferentes endpoints

### Passo 4: Testes Manuais

#### Testar Service A diretamente
```bash
# Listar usuários
curl http://localhost:5001/users

# Buscar usuário específico
curl http://localhost:5001/users/1

# Criar novo usuário
curl -X POST http://localhost:5001/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Novo Usuário",
    "email": "novo@email.com",
    "role": "developer",
    "department": "Engineering"
  }'

# Estatísticas
curl http://localhost:5001/stats
```

#### Testar Service B (que consome A)
```bash
# Usuários com informações agregadas
curl http://localhost:5002/users-info

# Info completa de um usuário
curl http://localhost:5002/users-info/1

# Apenas usuários ativos
curl http://localhost:5002/active-users

# Resumo de um usuário
curl http://localhost:5002/user-summary/1

# Estatísticas agregadas
curl http://localhost:5002/stats
```

### Passo 5: Ver logs de comunicação
```bash
# Logs do Service A (veja requisições recebidas)
docker logs -f service-a

# Logs do Service B (veja requisições enviadas ao A)
docker logs -f service-b

# Veja as chamadas HTTP entre serviços!
```

### Passo 6: Parar os serviços
```bash
./stop.sh
```

## 📝 Exemplos de Saída

### Service A - Listar Usuários:
```json
{
  "total": 5,
  "users": [
    {
      "id": "1",
      "name": "Alice Silva",
      "email": "alice.silva@email.com",
      "role": "developer",
      "active_since": "2023-01-15",
      "department": "Engineering",
      "status": "active"
    }
  ]
}
```

### Service B - Usuários Agregados:
```json
{
  "total": 5,
  "users": [
    {
      "id": "1",
      "name": "Alice Silva",
      "email": "alice.silva@email.com",
      "role": "developer",
      "department": "Engineering",
      "status": "active",
      "active_since": "2023-01-15",
      "activity": {
        "last_login": "2025-11-18 14:30:00",
        "total_logins": 245,
        "projects": 8
      },
      "days_active": 673,
      "engagement_level": "high"
    }
  ],
  "aggregated_by": "service-b"
}
```

### Service B - Resumo Executivo:
```json
{
  "user_id": "1",
  "name": "Alice Silva",
  "summary": "Alice Silva é developer no departamento de Engineering, ativo desde 2023-01-15 (673 dias). Realizou 245 logins e trabalha em 8 projetos. Nível de engajamento: high.",
  "status": "active",
  "engagement_level": "high"
}
```

### Logs mostrando comunicação:
```
# Service B
2025-11-19 10:30:00 - INFO - 📡 Chamando Serviço A: GET http://service-a:5001/users
2025-11-19 10:30:00 - INFO - ✓ Resposta do Serviço A: 200
2025-11-19 10:30:00 - INFO - ✓ Agregadas informações de 5 usuários
```

## 🧪 Testes de Validação

### Teste 1: Service A funcionando independentemente
```bash
curl http://localhost:5001/users
```
✅ **Esperado**: Lista de usuários retornada

### Teste 2: Comunicação entre serviços
```bash
# Parar Service A
docker stop service-a

# Tentar acessar Service B
curl http://localhost:5002/users-info
# Deve retornar erro 503

# Reiniciar Service A
docker start service-a
sleep 3

# Tentar novamente
curl http://localhost:5002/users-info
# Deve funcionar
```
✅ **Esperado**: Service B depende do Service A

### Teste 3: Verificar agregação de dados
```bash
# Comparar respostas
curl http://localhost:5001/users/1 > service-a-response.json
curl http://localhost:5002/users-info/1 > service-b-response.json

# Service B deve ter mais campos (activity, days_active, engagement_level)
```
✅ **Esperado**: Service B tem dados adicionais

### Teste 4: Health Check em cascata
```bash
curl http://localhost:5002/health | python3 -m json.tool
```
✅ **Esperado**: Mostra saúde de ambos os serviços

### Teste 5: Criar usuário no A e ver no B
```bash
# Criar no Service A
curl -X POST http://localhost:5001/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Teste", "email": "teste@email.com", "role": "tester", "department": "QA"}'

# Ver no Service B
curl http://localhost:5002/users-info | grep "Teste"
```
✅ **Esperado**: Novo usuário aparece em ambos

## 🎯 Pontos de Avaliação

### ✅ Funcionamento da comunicação entre microsserviços (5 pts)
- Service B faz requisições HTTP ao Service A
- Comunicação via rede Docker
- Logs mostram troca de mensagens
- Resiliência com tratamento de erros

### ✅ Dockerfiles e isolamento corretos (5 pts)
- Cada serviço tem seu próprio Dockerfile
- Imagens independentes
- Dependências isoladas
- Containers separados

### ✅ Explicação clara da arquitetura e endpoints (5 pts)
- Diagrama de arquitetura
- Documentação de todos endpoints
- Fluxo de dados explicado
- Exemplos de uso

### ✅ Clareza e originalidade da implementação (5 pts)
- Código bem estruturado e comentado
- Pattern Aggregator implementado
- Tratamento robusto de erros
- Logs informativos

## 🔍 Detalhes de Implementação

### Estrutura do Projeto
```
desafio4/
├── service-a/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── service-b/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── run.sh
├── test-services.sh
├── stop.sh
└── README.md
```

### Tratamento de Erros no Service B

```python
def call_service_a(endpoint):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Erro de conexão com Serviço A")
        return None
    except requests.exceptions.Timeout:
        logger.error("Timeout ao chamar Serviço A")
        return None
```

**Vantagens:**
- Service B não quebra se A estiver indisponível
- Retorna erro apropriado ao cliente
- Logs facilitam debugging

### Métricas Calculadas

```python
# Dias ativo
days_active = (datetime.now() - start_date).days

# Nível de engajamento
score = (total_logins / 10) + (projects * 10)
if score >= 100: return "high"
elif score >= 50: return "medium"
else: return "low"

# Média de logins
average = total_logins / days_active
```

## 🛠️ Troubleshooting

### Problema: Service B não consegue conectar ao A
```bash
# Verificar se ambos estão na mesma rede
docker network inspect desafio4-network

# Testar DNS
docker exec service-b ping -c 3 service-a

# Ver logs
docker logs service-b
```

### Problema: Portas já em uso
```bash
# Verificar processos usando as portas
lsof -i :5001
lsof -i :5002

# Parar processos ou usar portas diferentes
```

### Problema: Timeout nas requisições
```bash
# Aumentar timeout no código
response = requests.get(url, timeout=30)  # 30 segundos

# Ou verificar se Service A está lento
docker stats service-a
```

## 📚 Conceitos Demonstrados

1. **Microservices Architecture**: Serviços independentes e especializados
2. **HTTP/REST Communication**: Comunicação via API REST
3. **Service Discovery**: Resolução DNS no Docker
4. **Aggregator Pattern**: Combinar dados de múltiplas fontes
5. **Error Handling**: Tratamento robusto de falhas de rede
6. **Health Checks**: Monitoramento de saúde dos serviços
7. **Separation of Concerns**: Cada serviço com responsabilidade única
8. **API Design**: REST APIs bem estruturadas
9. **Logging**: Rastreabilidade de requisições
10. **Containerization**: Isolamento e portabilidade

## 🎓 Aprendizados

### Microsserviços vs Monolito

**Monolito:**
- ❌ Tudo em um único processo
- ❌ Difícil escalar partes específicas
- ❌ Deployment "all or nothing"

**Microsserviços:**
- ✅ Serviços independentes
- ✅ Escala granular
- ✅ Deploy independente
- ✅ Tecnologias diferentes por serviço

### Quando usar Microsserviços?
- ✅ Aplicações grandes e complexas
- ✅ Times distribuídos
- ✅ Necessidade de escalabilidade granular
- ✅ Deploy frequente de partes específicas

### Desafios dos Microsserviços
- ⚠️ Complexidade de rede
- ⚠️ Debugging distribuído
- ⚠️ Consistência de dados
- ⚠️ Latência de rede

### Boas Práticas Implementadas
1. **Timeouts**: Sempre definir timeout em requisições
2. **Health Checks**: Monitorar dependências
3. **Logging**: Rastrear requisições entre serviços
4. **Error Handling**: Falhar gracefully
5. **API Contracts**: Documentar endpoints claramente

---

**Autor**: Arthur Campos  
**Data**: Novembro 2025  
**Tecnologias**: Docker, Flask, Python Requests, REST APIs
