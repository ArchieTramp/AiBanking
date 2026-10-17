FROM python:3.12-slim

# Копируем uv из официального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Сначала копируем только файлы зависимостей для кэширования слоев
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (без установки самого проекта)
RUN uv sync --frozen --no-install-project --no-dev

# Копируем остальной код
COPY . .

# Запускаем приложение
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]