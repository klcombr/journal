FROM python:3.13-slim

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY journal_server ./journal_server

ENV JOURNAL_DB=/data/journal.db
VOLUME ["/data"]

EXPOSE 8000
CMD ["uvicorn", "journal_server.app:app", "--host", "0.0.0.0", "--port", "8000"]
