# SensAI demo deployment: one container with the web app, the API and both models.
# Stage 1 builds the React frontend; stage 2 runs FastAPI with the trained models.

FROM node:22-slim AS web
WORKDIR /web
COPY pilot/web/package.json pilot/web/package-lock.json ./
RUN npm ci
COPY pilot/web/ ./
RUN npm run build

FROM python:3.11-slim
RUN useradd -m -u 1000 user
WORKDIR /app
# Runtime dependencies only (CPU PyTorch; versions match the ones the models were saved with).
RUN pip install --no-cache-dir torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir stable-baselines3==2.9.0 gymnasium==1.3.0 numpy==2.4.6 \
        scikit-learn==1.9.1 joblib==1.6.0 fastapi==0.141.1 uvicorn==0.52.0 pydantic==2.13.4
COPY environment/ environment/
COPY models/ models/
COPY logs/ logs/
COPY pilot/ pilot/
COPY --from=web /web/dist pilot/web/dist
# Demo database lives in the container and is wiped on every restart: no real pilot data is ever here.
ENV PILOT_DB=/tmp/sensai-demo.sqlite3 PYTHONUNBUFFERED=1
USER user
EXPOSE 7860
# Refuse to start with the built-in development keys; the host (e.g. Render) sets PORT.
CMD ["sh", "-c", "test -n \"$PILOT_RESEARCHER_KEY\" && test -n \"$PILOT_OBSERVER_KEY\" || { echo 'Set PILOT_RESEARCHER_KEY and PILOT_OBSERVER_KEY'; exit 1; }; exec uvicorn pilot.server:app --host 0.0.0.0 --port ${PORT:-7860}"]
