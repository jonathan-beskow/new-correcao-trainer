# 🐍 Imagem base Python slim
FROM python:3.9-slim

# 📂 Define diretório de trabalho
WORKDIR /app

# 🛠️ Instala dependências de sistema necessárias
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    bash \
    build-essential \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# 📦 Instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 🧠 Copia todo o conteúdo da aplicação para dentro do container
COPY . .

# 🌐 Expõe a porta padrão do FastAPI
EXPOSE 8000

# 🚀 Inicia o servidor da aplicação FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
