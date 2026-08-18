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
    && python -m pip install --no-cache-dir \
        "https://github.com/aboul3la/Sublist3r/archive/6af1b8c22b5ca035818fbb04c54890896f9b181a.tar.gz" \
    && python -m pip install --no-cache-dir \
        "https://github.com/laramies/theHarvester/archive/refs/tags/4.11.1.tar.gz" \
    && python -m pip install --no-cache-dir .

VOLUME ["/workspace"]

# CENTAURUS is an on-demand CLI application, not a daemon.
# The default starts the conversational interface; callers may override the
# command with e.g. `centaurus investigate <natural-language request>`.
CMD ["centaurus", "shell"]
