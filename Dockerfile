FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

# Set timezone to Asia/Kolkata (IST) so 8 AM and 5 PM trigger at Indian Standard Time
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY config.py update_naukri.py scheduler.py ./

# Volumes: session.json, resumes/, logs/ are mounted from host
CMD ["python", "scheduler.py"]
