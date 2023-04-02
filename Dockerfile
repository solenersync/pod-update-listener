FROM python:3.9-slim

RUN pip install kubernetes requests

COPY pod_update_listener.py /app/

CMD ["python", "/app/update_listener.py"]