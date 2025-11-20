# Use official Python 3.12 image
FROM python:3.12.5-slim

# Install system dependencies needed for Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libasound2 \
    libnss3 \
    libxshmfence1 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    fonts-liberation \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better Docker caching)
COPY requirements.txt .

# Install Python dependencies (including Playwright)
RUN pip install --no-cache-dir -r requirements.txt

# Install ONLY Chromium browser for Playwright
RUN playwright install chromium

# Copy the rest of your project files
COPY . .

# Default command to start your app
CMD ["python3", "-m", "app.main"]
