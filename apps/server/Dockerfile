FROM python:3.13-slim

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY journal_server ./journal_server

# SQLite lives on the container filesystem. On Render's free tier that is
# ephemeral (lost on redeploy); with a persistent disk mounted at /data
# (starter plan), override this to JOURNAL_DB=/data/journal.db.
ENV JOURNAL_DB=/srv/journal.db

EXPOSE 8000
CMD ["uvicorn", "journal_server.app:app", "--host", "0.0.0.0", "--port", "8000"]
