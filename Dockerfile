FROM python:3.10-slim

WORKDIR /app

# Копируем зависимости из корня
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта (включая папку app)
COPY . .

# Указываем путь для импортов
ENV PYTHONPATH=/app

# Запуск: ищем main внутри папки app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]