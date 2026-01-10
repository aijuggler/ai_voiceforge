# Use an official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /main

# -------------------------------------------------
# Install ffmpeg (includes ffprobe)
# -------------------------------------------------
RUN apt-get update && apt-get install -y ffmpeg



# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend code
COPY . .

# -------------------------------------------------
# Ensure the output directory exists and is writable
# -------------------------------------------------
RUN mkdir -p /main/generated_podcasts && chmod -R 777 /main/generated_podcasts

# Expose the port FastAPI will run on
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]