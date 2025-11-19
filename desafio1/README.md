# Desafio 1 — Containers em Rede

## 📋 Descrição da Solução

Este desafio implementa dois containers Docker que se comunicam através de uma rede Docker customizada:

1. **Servidor Web (Flask)**: Um servidor HTTP que escuta na porta 8080 e responde a requisições
2. **Cliente HTTP**: Um cliente que realiza requisições periódicas ao servidor a cada 5 segundos

A comunicação entre os containers é feita através de uma rede Docker isolada chamada `desafio1-network`, permitindo que os containers se comuniquem usando nomes DNS ao invés de endereços IP.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│         Rede Docker: desafio1-network           │
│                                                 │
│  ┌──────────────────┐      ┌─────────────────┐ │
│  │   web-server     │◄─────┤  http-client    │ │
│  │                  │      │                 │ │
│  │  Flask Server    │      │  Python Script  │ │
│  │  Porta: 8080     │      │  (requests lib) │ │
│  └──────────────────┘      └─────────────────┘ │
│          │                                      │
└──────────┼──────────────────────────────────────┘
           │
           │ Port Mapping
           ▼
      Host: 8080
```

### Componentes da Solução:

#### 1. **Servidor Web (Flask)**
- **Tecnologia**: Python 3.11 + Flask
- **Porta**: 8080
- **Endpoints**:
  - `GET /`: Retorna informações sobre a requisição e contador
  - `GET /health`: Health check do servidor
  - `GET /stats`: Estatísticas de requisições
- **Funcionalidades**:
  - Registra logs de cada requisição recebida
  - Mantém contador de requisições
  - Retorna informações sobre timestamp, IP do cliente e nome do servidor

#### 2. **Cliente HTTP**
- **Tecnologia**: Python 3.11 + requests
- **Funcionalidades**:
  - Realiza requisições HTTP periódicas (a cada 5 segundos)
  - Implementa retry logic para aguardar o servidor estar pronto
  - Registra logs detalhados de cada requisição
  - Health check antes de iniciar as requisições

#### 3. **Rede Docker Customizada**
- **Nome**: `desafio1-network`
- **Driver**: bridge (padrão)
- **Função**: Isola os containers e permite comunicação por nome DNS

## 🔧 Decisões Técnicas

### Por que Flask?
- Framework leve e simples para criar APIs HTTP
- Excelente para demonstrar conceitos de rede e comunicação
- Fácil configuração de logging e middleware

### Por que Python?
- Linguagem clara e legível, facilitando o entendimento do código
- Bibliotecas robustas para HTTP (Flask e requests)
- Imagens Docker oficiais bem mantidas

### Rede Docker Customizada
- Permite isolamento dos containers
- DNS automático: containers podem se comunicar usando nomes ao invés de IPs
- Melhor controle sobre a comunicação entre serviços

### Retry Logic no Cliente
- Garante que o cliente aguarda o servidor estar pronto
- Evita falhas de conexão no início da execução
- Implementa uma experiência mais robusta

## 📊 Funcionamento Detalhado

### 1. **Criação da Rede**
```bash
docker network create desafio1-network
```
- Cria uma rede bridge isolada
- Containers conectados podem resolver nomes via DNS interno

### 2. **Build das Imagens**
```bash
docker build -t desafio1-server ./server
docker build -t desafio1-client ./client
```
- Cada container tem seu próprio Dockerfile
- Imagens baseadas em `python:3.11-slim` para menor tamanho
- Instalação de dependências via `requirements.txt`

### 3. **Execução do Servidor**
```bash
docker run -d \
    --name web-server \
    --network desafio1-network \
    -p 8080:8080 \
    desafio1-server
```
- `-d`: executa em background (detached)
- `--name web-server`: define o nome do container (usado para DNS)
- `--network desafio1-network`: conecta à rede customizada
- `-p 8080:8080`: mapeia porta do host para o container

### 4. **Execução do Cliente**
```bash
docker run -d \
    --name http-client \
    --network desafio1-network \
    desafio1-client
```
- Não precisa de mapeamento de porta (não recebe conexões externas)
- Conectado à mesma rede do servidor
- Usa `http://web-server:8080` para comunicação (resolução DNS)

### 5. **Fluxo de Comunicação**
1. Cliente faz requisição HTTP para `http://web-server:8080`
2. Docker DNS resolve `web-server` para o IP do container do servidor
3. Servidor recebe a requisição, processa e registra no log
4. Servidor retorna resposta JSON com informações
5. Cliente recebe resposta e exibe no log
6. Cliente aguarda 5 segundos e repete o processo

## 🚀 Instruções de Execução

### Pré-requisitos
- Docker instalado e rodando
- Bash (para executar os scripts)

### Passo 1: Dar permissão aos scripts
```bash
chmod +x run.sh stop.sh
```

### Passo 2: Executar o desafio
```bash
./run.sh
```

O script irá:
1. Limpar recursos anteriores (se existirem)
2. Criar a rede Docker customizada
3. Construir as imagens do servidor e cliente
4. Iniciar ambos os containers
5. Exibir os logs do cliente em tempo real

### Passo 3: Testar o servidor manualmente (opcional)
Em outro terminal:
```bash
# Testar endpoint principal
curl http://localhost:8080

# Testar health check
curl http://localhost:8080/health

# Testar estatísticas
curl http://localhost:8080/stats
```

### Passo 4: Visualizar logs
```bash
# Logs do servidor
docker logs -f web-server

# Logs do cliente
docker logs -f http-client

# Ver últimas 50 linhas dos logs do servidor
docker logs --tail 50 web-server
```

### Passo 5: Inspecionar a rede
```bash
# Ver detalhes da rede
docker network inspect desafio1-network

# Listar containers na rede
docker network inspect desafio1-network | grep Name
```

### Passo 6: Parar e limpar
```bash
./stop.sh
```

## 📝 Exemplo de Saída

### Logs do Servidor:
```
2025-11-18 10:30:15 - INFO - Iniciando servidor web na porta 8080...
2025-11-18 10:30:20 - INFO - Requisição #1 recebida de 172.18.0.3
2025-11-18 10:30:25 - INFO - Requisição #2 recebida de 172.18.0.3
2025-11-18 10:30:30 - INFO - Requisição #3 recebida de 172.18.0.3
```

### Logs do Cliente:
```
2025-11-18 10:30:18 - INFO - Cliente HTTP iniciado
2025-11-18 10:30:18 - INFO - Servidor alvo: http://web-server:8080
2025-11-18 10:30:18 - INFO - ✓ Servidor está pronto!
2025-11-18 10:30:20 - INFO - Enviando requisição para http://web-server:8080
2025-11-18 10:30:20 - INFO - ✓ Resposta recebida com sucesso!
2025-11-18 10:30:20 - INFO -   - Mensagem: Servidor Web está funcionando!
2025-11-18 10:30:20 - INFO -   - Número da requisição: 1
```

## 🧪 Testes e Validação

### Teste 1: Comunicação Básica
```bash
# Execute o run.sh e verifique se não há erros
./run.sh
```
✅ Esperado: Ambos os containers iniciam e logs mostram comunicação bem-sucedida

### Teste 2: Resolução DNS
```bash
# Entre no container do cliente e teste DNS
docker exec -it http-client ping -c 3 web-server
```
✅ Esperado: Ping bem-sucedido mostrando que o DNS está funcionando

### Teste 3: Acesso Externo
```bash
curl http://localhost:8080
```
✅ Esperado: Resposta JSON com status "success"

### Teste 4: Persistência de Logs
```bash
# Veja logs históricos mesmo após o container estar rodando há algum tempo
docker logs web-server
```
✅ Esperado: Histórico completo de todas as requisições

## 🎯 Pontos de Avaliação

### ✅ Configuração correta da rede Docker (5 pts)
- Rede customizada `desafio1-network` criada com sucesso
- Ambos containers conectados à mesma rede
- Isolamento adequado dos containers

### ✅ Comunicação funcional entre containers (5 pts)
- Cliente consegue resolver o nome `web-server` via DNS
- Requisições HTTP bem-sucedidas
- Logs mostram troca de mensagens bidirecional

### ✅ Explicação clara no README (5 pts)
- Arquitetura documentada com diagramas
- Decisões técnicas justificadas
- Fluxo de comunicação explicado em detalhes

### ✅ Organização do projeto e scripts de execução (5 pts)
- Estrutura de pastas clara (server/client)
- Scripts automatizados (run.sh, stop.sh)
- Dockerfiles bem estruturados
- Código com boas práticas e comentários

## 🔍 Detalhes de Implementação

### Dockerfile do Servidor
- Base: `python:3.11-slim` (imagem leve)
- Working directory: `/app`
- Dependências: Flask e Werkzeug
- Porta exposta: 8080
- Comando: `python app.py`

### Dockerfile do Cliente
- Base: `python:3.11-slim`
- Working directory: `/app`
- Dependências: requests e urllib3
- Comando: `python client.py`

### Características do Código Python

#### Servidor (app.py):
- **Logging estruturado**: Registra todas as requisições com timestamp
- **Contador global**: Mantém estatísticas de requisições
- **Múltiplos endpoints**: /, /health, /stats
- **Informações contextuais**: Retorna IP do cliente, timestamp, nome do servidor

#### Cliente (client.py):
- **Retry logic**: Tenta conectar 10 vezes antes de desistir
- **Health check**: Valida se servidor está pronto antes de requisições
- **Tratamento de erros**: Captura e loga diferentes tipos de exceção
- **Logging detalhado**: Mostra todas as informações da resposta

## 🛠️ Troubleshooting

### Problema: "Network already exists"
```bash
docker network rm desafio1-network
```

### Problema: "Port 8080 already in use"
```bash
# Encontrar processo usando a porta
lsof -i :8080
# Ou parar containers anteriores
docker stop web-server
```

### Problema: Cliente não consegue conectar
```bash
# Verificar se ambos estão na mesma rede
docker network inspect desafio1-network

# Verificar se servidor está rodando
docker ps | grep web-server

# Testar DNS manualmente
docker exec http-client nslookup web-server
```

## 📚 Conceitos Demonstrados

1. **Docker Networks**: Criação e uso de redes customizadas
2. **Service Discovery**: Resolução DNS entre containers
3. **Container Communication**: Comunicação HTTP entre containers
4. **Port Mapping**: Exposição de portas para o host
5. **Logging**: Implementação de logs estruturados
6. **Error Handling**: Tratamento robusto de erros de rede
7. **Dockerfiles**: Criação de imagens customizadas
8. **Bash Scripting**: Automação de tarefas Docker

## 🎓 Aprendizados

Este desafio demonstra conceitos fundamentais de:
- Isolamento e comunicação entre containers
- Redes Docker e resolução DNS interna
- Criação de aplicações distribuídas simples
- Boas práticas de logging e monitoramento
- Automação com shell scripts

---

**Autor**: Arthur Campos  
**Data**: Novembro 2025  
**Curso**: Computação em Nuvem e Programação Distribuída
