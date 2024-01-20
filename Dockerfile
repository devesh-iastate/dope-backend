# Use a specific, digest-pinned version of the python image for reproducibility
FROM python:3.10@sha256:your_specific_digest

# Define work directory
WORKDIR /app

# Install dependencies
# Copying the requirements file and installing dependencies as a separate step
# Utilizes Docker's cache to speed up builds if the requirements haven't changed
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy the source code into the image
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Specify the command to run your app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
