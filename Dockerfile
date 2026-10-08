FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN mkdir -p /app/data/uploads && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "sentinelia.main:app", "--host", "0.0.0.0", "--port", "8000"]

