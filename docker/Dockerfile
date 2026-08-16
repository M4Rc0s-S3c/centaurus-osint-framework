FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CENTAURUS_WORKSPACE=/workspace \
    OLLAMA_BASE_URL=http://centaurus-ollama:11434

WORKDIR /opt/centaurus

COPY pyproject.toml ./
COPY src ./src

RUN python -m pip install --no-cache-dir \
        "https://github.com/darkoperator/dnsrecon/archive/refs/tags/1.6.3.tar.gz" \
    && python -m pip install --no-cache-dir .

VOLUME ["/workspace"]

# The framework is currently an on-demand CLI/application container, not a daemon.
# This default command validates that the framework can be constructed inside the image;
# operational CLI wiring can replace it without changing the deployment boundary.
CMD ["python", "-c", "from centaurus.core import Core; core = Core(); core.initialize(); print('CENTAURUS framework initialized')"]
