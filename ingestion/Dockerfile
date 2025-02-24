# Use official Python 3.11 image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the container
COPY . .

# Install dependencies if requirements.txt exists
RUN pip install --no-cache-dir -r requirements_venv.txt || true

# # Set the default command to run the script
CMD ["python", "pea_reg.py"]
# CMD ["python", "test_connect_milvus.py"]
