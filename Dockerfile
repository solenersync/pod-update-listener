FROM python:3.9-slim

RUN pip install kubernetes requests

COPY pod-update-listener.py /app/

CMD ["python", "/app/pod-update-listener.py"]