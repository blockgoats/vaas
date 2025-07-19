FROM python:3.11-slim

# Set working directory inside container
WORKDIR /

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . ./

# Set the PYTHONPATH so that 'app' is a root-level package
ENV PYTHONPATH=/

# Run FastAPI with hot reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
