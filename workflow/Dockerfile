FROM python:3.13-slim
RUN python -m pip install --no-cache-dir pytest==9.1.1 setuptools==82.0.1 wheel==0.46.3
COPY run_checks.py /opt/autose/run_checks.py
ENTRYPOINT ["python", "/opt/autose/run_checks.py"]
