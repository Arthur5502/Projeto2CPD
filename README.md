# 🚀 Projeto 2 - Computação em Nuvem e DevOps

## 📚 Sobre o Projeto

Este projeto implementa **5 desafios progressivos** sobre **Docker, microsserviços e orquestração de containers**, demonstrando desde conceitos básicos de networking até arquiteturas avançadas com API Gateway.

Desenvolvido como projeto acadêmico para a disciplina de **Computação em Nuvem e DevOps**, cada desafio aumenta gradativamente em complexidade, apresentando boas práticas de código, documentação detalhada e scripts automatizados.

**Pontuação Total**: 110 pontos

---

## 📂 Estrutura do Projeto

```
Projeto2CPD/
│
├── desafio1/              # Containers em Rede (20 pts)
│   ├── server/            # Servidor web Flask
│   ├── client/            # Cliente que consome o servidor
│   ├── run.sh             # Script automatizado
│   └── README.md          # Documentação detalhada
│
├── desafio2/              # Volumes e Persistência de Dados (20 pts)
│   ├── app/               # Aplicação de tarefas
│   ├── reader/            # Leitor que valida persistência
│   ├── run.sh             # Script automatizado
│   ├── test-persistence.sh  # Teste de persistência
│   └── README.md          # Documentação detalhada
│
├── desafio3/              # Docker Compose (25 pts)
│   ├── web/               # API de produtos
│   ├── db/                # PostgreSQL com init script
│   ├── docker-compose.yml # Orquestração de 3 serviços
│   ├── run.sh             # Script automatizado
│   ├── test-api.sh        # Teste da API
│   └── README.md          # Documentação detalhada
│
├── desafio4/              # Microsserviços Independentes (20 pts)
│   ├── service-a/         # Serviço de Usuários
│   ├── service-b/         # Serviço Agregador
│   ├── run.sh             # Script automatizado
│   ├── test-services.sh   # Teste de comunicação
│   └── README.md          # Documentação detalhada
│
├── desafio5/              # Microsserviços com API Gateway (25 pts)
│   ├── gateway/           # API Gateway (ponto único de entrada)
│   ├── users-service/     # Microsserviço de usuários
│   ├── orders-service/    # Microsserviço de pedidos
│   ├── docker-compose.yml # Orquestração completa
│   ├── run.sh             # Script automatizado
│   ├── test-gateway.sh    # Teste do gateway
│   └── README.md          # Documentação detalhada
│
└── README.md              # Este arquivo
```

---

## 🎯 Descrição dos Desafios

### **Desafio 1 — Containers em Rede** (20 pontos)

**Objetivo**: Criar dois containers Docker que se comunicam através de uma rede customizada.

**Componentes**:
- **Servidor**: Flask na porta 8080, responde requisições HTTP
- **Cliente**: Python script que faz requisições ao servidor
- **Rede**: `desafio1-network` (bridge)

**Conceitos**:
- Docker networking
- Comunicação entre containers
- Resolução DNS interna do Docker

**Como executar**: `cd desafio1 && ./run.sh`

---

### **Desafio 2 — Volumes e Persistência de Dados** (20 pontos)

**Objetivo**: Demonstrar persistência de dados com Docker volumes.

**Componentes**:
- **Aplicação**: CRUD de tarefas com PostgreSQL
- **Banco de dados**: PostgreSQL com volume persistente
- **Reader**: Valida que dados sobrevivem à recriação do container

**Conceitos**:
- Docker volumes
- Persistência de dados
- Banco de dados em containers
- Validação de persistência

**Como executar**: `cd desafio2 && ./run.sh`  
**Testar persistência**: `./test-persistence.sh`

---

### **Desafio 3 — Docker Compose** (25 pontos)

**Objetivo**: Orquestrar 3 serviços interdependentes com Docker Compose.

**Componentes**:
- **Web**: API REST de produtos com cache
- **Database**: PostgreSQL com initialization script
- **Cache**: Redis para otimização de performance

**Conceitos**:
- Docker Compose
- Orquestração de serviços
- Health checks
- Depends_on com condition
- Cache-aside pattern
- Service dependencies

**Como executar**: `cd desafio3 && ./run.sh`  
**Testar API**: `./test-api.sh`

---

### **Desafio 4 — Microsserviços Independentes** (20 pontos)

**Objetivo**: Implementar dois microsserviços que se comunicam via HTTP.

**Componentes**:
- **Service A (Users)**: CRUD de usuários (porta 5001)
- **Service B (Aggregator)**: Agrega dados de atividades (porta 5002)
- **Comunicação**: HTTP requests entre serviços

**Conceitos**:
- Arquitetura de microsserviços
- Comunicação service-to-service
- APIs REST
- Service discovery

**Como executar**: `cd desafio4 && ./run.sh`  
**Testar comunicação**: `./test-services.sh`

---

### **Desafio 5 — Microsserviços com API Gateway** (25 pontos)

**Objetivo**: Implementar arquitetura completa com API Gateway como ponto único de entrada.

**Componentes**:
- **API Gateway**: Roteamento e agregação (porta 8000)
- **Users Service**: Gerenciamento de usuários (porta interna 5001)
- **Orders Service**: Gerenciamento de pedidos (porta interna 5003)

**Conceitos**:
- API Gateway Pattern
- Gateway Routing
- Gateway Aggregation
- Service Orchestration
- Segurança (serviços não expostos externamente)

**Como executar**: `cd desafio5 && ./run.sh`  
**Testar gateway**: `./test-gateway.sh`

---

## 🔧 Tecnologias Utilizadas

### Core
- **Docker**: Containerização de aplicações
- **Docker Compose**: Orquestração de múltiplos containers
- **Python 3.11**: Linguagem principal
- **Flask**: Framework web para APIs REST

### Bancos de Dados & Cache
- **PostgreSQL 15-alpine**: Banco relacional
- **Redis 7-alpine**: Cache em memória

### Bibliotecas Python
- **Flask 3.0.0**: Framework web
- **requests 2.31.0**: Cliente HTTP
- **psycopg2-binary**: Driver PostgreSQL
- **redis**: Cliente Redis Python

### Ferramentas
- **Bash**: Scripts de automação
- **curl**: Testes de API
- **jq**: Manipulação de JSON (opcional)

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

Certifique-se de ter instalado:
- **Docker** (20.10 ou superior)
- **Docker Compose** (2.0 ou superior)

Para verificar:
```bash
docker --version
docker compose version
```

### Executar Todos os Desafios

Cada desafio é independente. Para executar:

```bash
# Desafio 1
cd desafio1
chmod +x run.sh stop.sh
./run.sh

# Desafio 2
cd ../desafio2
chmod +x run.sh stop.sh test-persistence.sh
./run.sh

# Desafio 3
cd ../desafio3
chmod +x run.sh stop.sh test-api.sh
./run.sh

# Desafio 4
cd ../desafio4
chmod +x run.sh stop.sh test-services.sh
./run.sh

# Desafio 5
cd ../desafio5
chmod +x run.sh stop.sh test-gateway.sh
./run.sh
```

### Parar Todos os Serviços

Cada desafio tem seu script `stop.sh`:

```bash
# Em cada diretório
./stop.sh
```

---

## 📊 Pontuação por Desafio

| Desafio | Descrição | Pontos |
|---------|-----------|--------|
| **1** | Containers em Rede | 20 |
| **2** | Volumes e Persistência | 20 |
| **3** | Docker Compose | 25 |
| **4** | Microsserviços Independentes | 20 |
| **5** | API Gateway | 25 |
| **TOTAL** | | **110** |

### Critérios de Avaliação

Cada desafio é avaliado com base em:

1. **Funcionalidade** (40-50%): Código funciona conforme especificado
2. **Integração** (20-25%): Serviços se comunicam corretamente
3. **Documentação** (20-25%): README detalhado com explicações
4. **Qualidade do Código** (20-25%): Organização, clareza e boas práticas

---

## 📖 Documentação Detalhada

Cada desafio possui um **README.md completo** com:

- ✅ Descrição da solução
- ✅ Arquitetura e diagramas
- ✅ Decisões técnicas
- ✅ Instruções passo a passo
- ✅ Exemplos de uso
- ✅ Testes automatizados
- ✅ Conceitos demonstrados

**Navegue para cada diretório para acessar a documentação específica.**

---

## 🎓 Conceitos Implementados

### Docker Fundamentals
- ✅ Dockerfile multi-stage (otimização)
- ✅ Docker networking (bridge, custom networks)
- ✅ Docker volumes (persistência)
- ✅ Container lifecycle management
- ✅ Port mapping e exposure

### Docker Compose
- ✅ Multi-container orchestration
- ✅ Service dependencies (depends_on)
- ✅ Health checks
- ✅ Volume management
- ✅ Network isolation

### Arquitetura de Software
- ✅ Microsserviços
- ✅ API Gateway Pattern
- ✅ Service-to-Service Communication
- ✅ Cache-aside Pattern
- ✅ Gateway Routing & Aggregation

### APIs REST
- ✅ CRUD operations
- ✅ HTTP methods (GET, POST, PUT, DELETE)
- ✅ Status codes corretos
- ✅ JSON responses
- ✅ Error handling

### Best Practices
- ✅ Clean code
- ✅ Separation of concerns
- ✅ Configuration via environment variables
- ✅ Logging estruturado
- ✅ Graceful error handling
- ✅ Health check endpoints

---

## 🧪 Testes

Cada desafio inclui scripts de teste:

```bash
# Desafio 1 - Teste manual
curl http://localhost:8080

# Desafio 2 - Teste de persistência
./test-persistence.sh

# Desafio 3 - Teste da API
./test-api.sh

# Desafio 4 - Teste de comunicação entre serviços
./test-services.sh

# Desafio 5 - Teste do API Gateway
./test-gateway.sh
```

---

## 🔍 Troubleshooting

### Problema: Porta já em uso
```bash
# Ver processos usando a porta
lsof -i :8080

# Parar todos os containers
docker compose down
```

### Problema: Volume com permissões incorretas
```bash
# Remover volume e recriar
docker volume rm nome_do_volume
```

### Problema: Imagem não atualizada
```bash
# Rebuild forçado
docker compose build --no-cache
```

### Ver logs de um serviço
```bash
docker compose logs -f nome_do_servico
```

---

## 🎯 Progressão de Aprendizado

```
Desafio 1: Networking Básico
    ↓
Desafio 2: Persistência de Dados
    ↓
Desafio 3: Orquestração Multi-Container
    ↓
Desafio 4: Comunicação entre Microsserviços
    ↓
Desafio 5: Arquitetura Completa com Gateway
```

Cada desafio constrói sobre os conceitos anteriores, criando uma **curva de aprendizado incremental** que culmina em uma arquitetura de microsserviços completa e production-ready.

---

## 📝 Estrutura de Código

Todos os desafios seguem a mesma estrutura organizada:

```
desafioX/
├── service/               # Código da aplicação
│   ├── app.py            # Código principal
│   ├── requirements.txt  # Dependências Python
│   └── Dockerfile        # Definição do container
│
├── docker-compose.yml    # Orquestração (desafios 3 e 5)
├── run.sh                # Script de inicialização
├── stop.sh               # Script de limpeza
├── test-*.sh             # Scripts de teste
└── README.md             # Documentação completa
```

---

## 🌟 Diferenciais do Projeto

✨ **Código Production-Ready**:
- Error handling robusto
- Logging estruturado
- Health checks implementados
- Timeouts configurados

✨ **Documentação Excepcional**:
- READMEs detalhados
- Diagramas de arquitetura
- Exemplos de uso
- Conceitos explicados

✨ **Automação Completa**:
- Scripts para todas as operações
- Testes automatizados
- Setup com um comando

✨ **Boas Práticas**:
- Clean code
- Separation of concerns
- Configuração via environment variables
- Minimal Docker images

---

## 👨‍💻 Autor

**Arthur Campos**  
Novembro 2025  

Projeto desenvolvido como parte da disciplina de **Computação em Nuvem e DevOps**.

---

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Microservices Patterns](https://microservices.io/patterns/)
- [API Gateway Pattern](https://microservices.io/patterns/apigateway.html)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)

---

## 🎓 Aprendizados e Conclusões

Este projeto demonstra a **evolução natural** de aplicações monolíticas para arquiteturas de microsserviços:

1. **Comunicação básica** entre containers (Desafio 1)
2. **Persistência** adequada de dados (Desafio 2)
3. **Orquestração** de múltiplos serviços (Desafio 3)
4. **Decomposição** em microsserviços independentes (Desafio 4)
5. **Centralização** com API Gateway (Desafio 5)

Cada camada adiciona **complexidade controlada**, preparando para arquiteturas cloud-native reais utilizadas na indústria.

---

## 📄 Licença

Este projeto é de uso acadêmico. Desenvolvido para fins educacionais.

---

**🚀 Pronto para explorar? Comece pelo Desafio 1 e avance progressivamente!**

```bash
cd desafio1 && ./run.sh
```