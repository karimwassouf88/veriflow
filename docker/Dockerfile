FROM python:3.12-slim
WORKDIR /code
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock* /code/
RUN uv sync --no-dev
COPY app /code/app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]