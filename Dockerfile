# Gunakan base image Python 3.12.4
FROM python:3.12.4-slim

# Install OS dependencies (tambahkan jika perlu)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy semua file ke dalam container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Port yang digunakan (ikuti Cloud Run: 8080)
ENV PORT=8080
EXPOSE 8080

# Jalankan Streamlit pada port 8080 (baca dari $PORT)
CMD ["sh", "-c", "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false"]
