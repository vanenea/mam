FROM python:3.11-slim

# Copy uv binaries from the distroless image
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

# 在运行镜像内创建 venv，避免跨镜像复制导致解释器版本不一致
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-cache --no-install-project

COPY --chown=nobody:nogroup . .

RUN rm -f /app/finance.db

RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; prefix = os.environ.get('MAM_BASE_PATH', '').rstrip('/'); urllib.request.urlopen(f'http://localhost:5000{prefix}/login', timeout=5)" || exit 1

# 直接使用 venv 中的 python，避免 uv run 在启动时重新同步环境（需要联网）
CMD ["python", "main.py"]