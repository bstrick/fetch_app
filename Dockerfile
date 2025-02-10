FROM python:3.8-slim
WORKDIR /fetch_app
COPY . .
# Installing dependencies
RUN pip3 install --upgrade pip && pip install --no-cache-dir -r req.txt
# Expose port 5000 for calls
EXPOSE 5000
#Command to run the app
CMD ["python", "app.py", "-p", "5000:5000"]