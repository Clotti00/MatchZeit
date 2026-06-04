# app/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# --- Layer 1: System Dependencies (if needed) ---
# RUN apt-get update && apt-get install -y \
#    build-essential \
#    curl \
#    software-properties-common \
#    git \
#    && rm -rf /var/lib/apt/lists/*

# --- Layer 2: Python Dependencies (Cached) ---
# Copy ONLY the requirements file first
COPY requirements.txt .

# Install dependencies. They will remain cached unless requirements.txt changes.
RUN pip3 install --no-cache-dir -r requirements.txt

# --- Layer 3: Application Code ---
# Copy the rest of your code. Code changes will only invalidate this layer and below.
COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
