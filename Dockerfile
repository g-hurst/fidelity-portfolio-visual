FROM python:3.11-slim

# Install packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app
workdir /app

# Expose the port the Dash app will run on
EXPOSE 8050

# Command to run your Dash app
CMD ["python", "app.py"]