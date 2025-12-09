FROM python:3.10-alpine

# Set the working directory inside the container
WORKDIR /usr/src/Alarm

# Copy the Python script and requirements file into the container
COPY main.py .
COPY requirements.txt .
RUN pip3 install --upgrade pip
# Install Python dependencies
RUN pip3 install -r requirements.txt
EXPOSE 8090
# Specify the default command to run when the container starts
CMD ["python", "main.py"]
