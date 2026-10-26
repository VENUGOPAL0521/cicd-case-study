# OrderService CI/CD Pipeline — Run Locally

This folder contains every code artifact from the case study, separated out so you can run
each piece directly on your own machine.

```
app/main.py                          # The Flask microservice
app/requirements.txt                 # Its one dependency (flask)
tests/test_main.py                   # 6-case pytest suite
Dockerfile                           # Container build definition
.github/workflows/ci-cd-pipeline.yml # The 5-stage GitHub Actions pipeline
k8s/staging/deployment.yaml          # Staging Kubernetes manifest
k8s/production/canary-10.yaml        # Production canary Kubernetes manifest
```

## 1. Run the app locally (no Docker needed)

Requires Python 3.9+.

```bash
cd app
pip install -r requirements.txt
python main.py
```

The service starts on **http://localhost:8080**. Try it in another terminal:

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/orders -H "Content-Type: application/json" -d '{"item":"Laptop","quantity":2}'
```

## 2. Run the tests

```bash
pip install -r app/requirements.txt pytest pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```

You should see 6 passed and ~96% coverage.

## 3. Build and run the container (requires Docker Desktop / Docker Engine)

From the project root (same folder as this README):

```bash
docker build -t orderservice:local .
docker run -p 8080:8080 orderservice:local
```

Then hit the same `curl` commands as above.

## 4. Use the CI/CD pipeline on GitHub

1. Create a new GitHub repo and push this whole folder to it (the `.github/workflows/`
   folder must sit at the repo root — GitHub auto-detects it).
2. Go to **Settings → Environments** and create two environments named `staging` and
   `production` (add a required reviewer on `production` if you want the manual approval
   gate to actually pause the pipeline there).
3. Push a commit — the `lint`, `test`, and `build` jobs will run automatically. The
   `deploy-staging` and `deploy-production` jobs contain placeholder `kubectl`/monitoring
   commands (commented explanations inline) since they assume a real cluster and registry
   — swap in your own cluster credentials as GitHub Actions secrets to make them live.

## 5. Apply the Kubernetes manifests (requires a real cluster + kubectl configured)

```bash
kubectl apply -f k8s/staging/deployment.yaml
kubectl apply -f k8s/production/canary-10.yaml
```

Update the `image:` fields in both files to point at your own registry/image tag first.
