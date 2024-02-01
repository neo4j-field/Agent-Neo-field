docker build --platform linux/amd64 -t agent-neo-backend .

docker tag agent-neo-backend us-central1-docker.pkg.dev/sales-eng-agent-neo-project/agent-neo/agent-neo-backend

docker push us-central1-docker.pkg.dev/sales-eng-agent-neo-project/agent-neo/agent-neo-backend