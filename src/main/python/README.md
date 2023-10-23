



## Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed on your system.
- GCP Service Account Key. Ensure you have this file: `Agent-Neo-field/src/main/python/resources/gcp_service_account.json`. If it's in a different location, update the Docker run command accordingly.

## Steps to Build and Run

### 1. Clone the Repository:

```bash
git clone [URL-to-your-repository]
cd [your-repository-name] 
```


### 2. Build the Image

```bash
docker build -t neoagent_backend .
```

### 3. Run the container
```bash
docker run -v /Users/alexanderfournier/Downloads/Agent-Neo-field/src/main/python/resources/gcp_service_account.json:/path/in/container/gcp_service_account.json neoagent_backend
```