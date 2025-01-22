# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AWS_REGION=us-east-1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN apt-get -y update; apt-get -y install curl
RUN apt-get update && apt-get install -y ca-certificates
RUN update-ca-certificates
RUN apt-get update && apt-get install -y ntp

# Copy the application code
COPY . /app/

# Expose the required port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

ENTRYPOINT ["sh", "-c", "date && exec \"$@\"", "--"]


#Docker - ECR login and create repository
#aws ecr get-login-password --region us-east-1 --debug | docker login --username AWS --password-stdin 352071936583.dkr.ecr.us-east-1.amazonaws.com
#aws ecr create-repository --repository-name nmbs-rag-api --region us-east-1

#sudo docker build -t nmbs-rag-api .
#docker tag nmbs-rag-api 352071936583.dkr.ecr.us-east-1.amazonaws.com/nmbs-rag-api:v0.1
#docker push 352071936583.dkr.ecr.us-east-1.amazonaws.com/nmbs-rag-api:v0.1
#Test the docker API container locally
#aws sts assume-role --role-arn arn:aws:iam::352071936583:role/nmbs-ecs-role --role-session-name LocalTestingSession
#docker run -e AWS_REGION=us-east-1 -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN -p 8000:8000 --name nmbs-api -d nmbs-rag-api:latest