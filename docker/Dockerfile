FROM python:3.12.14-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CENTAURUS_WORKSPACE=/workspace \
    OLLAMA_BASE_URL=http://centaurus-ollama:11434 \
    HOME=/home/centaurus

WORKDIR /opt/centaurus

COPY pyproject.toml ./
COPY requirements-core.lock ./
COPY requirements-dnsrecon.lock ./locks/
COPY requirements-sublist3r.lock ./locks/
COPY requirements-theharvester.lock ./locks/
COPY src ./src

RUN set -eux; \
    python -m pip install --no-cache-dir -r requirements-core.lock; \
    python -m pip install --no-cache-dir --no-deps .; \
    python -m pip check; \
    mkdir -p /opt/centaurus-tools; \
    python -m venv /opt/centaurus-tools/dnsrecon; \
    /opt/centaurus-tools/dnsrecon/bin/python -m pip install --no-cache-dir "setuptools==83.0.0"; \
    /opt/centaurus-tools/dnsrecon/bin/python -m pip install --no-cache-dir --no-build-isolation -r /opt/centaurus/locks/requirements-dnsrecon.lock; \
    /opt/centaurus-tools/dnsrecon/bin/python -m pip check; \
    python -m venv /opt/centaurus-tools/sublist3r; \
    /opt/centaurus-tools/sublist3r/bin/python -m pip install --no-cache-dir "setuptools==83.0.0"; \
    /opt/centaurus-tools/sublist3r/bin/python -m pip install --no-cache-dir --no-build-isolation -r /opt/centaurus/locks/requirements-sublist3r.lock; \
    /opt/centaurus-tools/sublist3r/bin/python -m pip check; \
    python -m venv /opt/centaurus-tools/theharvester; \
    /opt/centaurus-tools/theharvester/bin/python -m pip install --no-cache-dir "setuptools==83.0.0" "flit_core==3.12.0"; \
    /opt/centaurus-tools/theharvester/bin/python -m pip install --no-cache-dir --no-build-isolation -r /opt/centaurus/locks/requirements-theharvester.lock; \
    /opt/centaurus-tools/theharvester/bin/python -m pip check; \
    ln -s /opt/centaurus-tools/dnsrecon/bin/dnsrecon /usr/local/bin/dnsrecon; \
    ln -s /opt/centaurus-tools/sublist3r/bin/sublist3r /usr/local/bin/sublist3r; \
    ln -s /opt/centaurus-tools/theharvester/bin/theHarvester /usr/local/bin/theHarvester; \
    python -m pip check; \
    groupadd --gid 1000 centaurus; \
    useradd --uid 1000 --gid 1000 --create-home --shell /usr/sbin/nologin centaurus; \
    mkdir -p /workspace; \
    chown 1000:1000 /workspace

VOLUME ["/workspace"]

# R5: application runtime uses a fixed unprivileged identity. Host /workspace
# ownership is validated/migrated once by the deployment procedure.
USER 1000:1000

# CENTAURUS is an on-demand CLI application, not a daemon.
# The default starts the conversational interface; callers may override the
# command with e.g. `centaurus investigate <natural-language request>`.
CMD ["centaurus", "shell"]
