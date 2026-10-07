FROM python:3.11-slim

WORKDIR /app

# Копіюємо файл зі списком бібліотек
COPY requirements.txt .

# Встановлюємо їх
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо решту коду
COPY . .

# Запускаємо через модуль python -m, щоб точно не було помилок з PATH
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]