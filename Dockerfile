# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependency file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and their dependencies
RUN playwright install-deps
RUN playwright install

# Copy the rest of the application's code to the working directory
COPY . .

# Set the entrypoint for the container
ENTRYPOINT ["/app/run_scanner.sh"]
