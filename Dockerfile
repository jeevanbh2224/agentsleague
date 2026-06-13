FROM python:3.11-slim

# Non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY --chown=app:app . .

# Create generated images dir
RUN mkdir -p /app/generated/history && chown -R app:app /app/generated

USER app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run the HTTP API (not the interactive terminal game)
CMD ["python3", "api.py"]
