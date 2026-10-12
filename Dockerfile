FROM python:3.12-slim

# Evita .pyc e deixa os logs saírem na hora (importante pro docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Copia só as dependências primeiro, para aproveitar o cache de camadas
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Agora o código
COPY app/ app/

# Usuário não-root
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]