FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    TMPDIR=/tmp
WORKDIR /repo
COPY . /repo
RUN python -m pip install --no-cache-dir -e ".[evaluation,dev,core,orchestrator]" \
    && python -m pip freeze > /opt/dependencies.txt
USER 10001:10001
CMD ["python", "sandbox/run.py"]
