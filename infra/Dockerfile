FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml alembic.ini ./
COPY server ./server
COPY core ./core
COPY desktop ./desktop
COPY exporters ./exporters
RUN pip install --no-cache-dir .
RUN useradd --create-home agrolines
USER agrolines
EXPOSE 8000
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
