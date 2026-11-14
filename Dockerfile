FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

ENV MYCP_DB_PATH=/data/mycp.db \
    MYCP_HOST=0.0.0.0 \
    MYCP_PORT=8080

VOLUME ["/data"]
EXPOSE 8080
CMD ["mycp", "run"]
