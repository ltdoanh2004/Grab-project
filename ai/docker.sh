# Build the image
docker build -t ai-model .

# Run the container
docker run -d \
  --name ai-model \
  -p 8001:8001 \
  -v $(pwd)/model:/app \
  ai-model