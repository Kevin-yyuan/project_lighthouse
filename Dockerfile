# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run the application
CMD ["./start.sh"]