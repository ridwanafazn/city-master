# Gunakan base image Python 3.12.4
FROM python:3.12.4-slim

# Install OS-level dependencies (opsional: sesuaikan kalau app-mu perlu lib lain)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Salin semua file dari direktori saat ini ke container
COPY . /app

# Install dependencies Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port default Streamlit
EXPOSE 8501

# Jalankan Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
