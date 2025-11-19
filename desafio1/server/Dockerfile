# Dockerfile para o Servidor Web
# Usa Python 3.11 slim para ter uma imagem mais leve

FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY app.py .

# Expõe a porta 8080
EXPOSE 8080

# Define o comando para executar a aplicação
CMD ["python", "app.py"]
