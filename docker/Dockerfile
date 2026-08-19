FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CENTAURUS_WORKSPACE=/workspace \
    OLLAMA_BASE_URL=http://centaurus-ollama:11434 \
    HOME=/home/centaurus

WORKDIR /opt/centaurus

COPY pyproject.toml ./
COPY src ./src

RUN python -m pip install --no-cache-dir \
        "https://github.com/darkoperator/dnsrecon/archive/refs/tags/1.6.3.tar.gz" \
    && python -m pip install --no-cache-dir \
        "https://github.com/aboul3la/Sublist3r/archive/6af1b8c22b5ca035818fbb04c54890896f9b181a.tar.gz" \
    && python -m pip install --no-cache-dir \
        "https://github.com/laramies/theHarvester/archive/refs/tags/4.11.1.tar.gz" \
    && python -m pip install --no-cache-dir . \
    && groupadd --gid 1000 centaurus \
    && useradd --uid 1000 --gid 1000 --create-home --shell /usr/sbin/nologin centaurus \
    && mkdir -p /workspace \
    && chown 1000:1000 /workspace

VOLUME ["/workspace"]

# R5: application runtime uses a fixed unprivileged identity. Host /workspace
# ownership is validated/migrated once by the deployment procedure.
USER 1000:1000

# CENTAURUS is an on-demand CLI application, not a daemon.
# The default starts the conversational interface; callers may override the
# command with e.g. `centaurus investigate <natural-language request>`.
CMD ["centaurus", "shell"]
