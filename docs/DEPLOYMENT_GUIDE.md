# GCP Deployment Guide: Travel Planning & Experience Engine

This guide provides the exact commands needed to deploy the Travel Planning & Experience Engine to **Google Cloud Run**.

## Prerequisites
1. [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) installed.
2. An active GCP Billing Account.
3. Authenticated gcloud: `gcloud auth login`

---

## Step 1: Configuration
Set your project ID (using the one you provided earlier):
```bash
gcloud config set project promptwars-gurgaon
```

## Step 2: Enable APIs
Enable the necessary services for deployment:
```bash
gcloud services enable run.googleapis.com \
                       artifactregistry.googleapis.com \
                       cloudbuild.googleapis.com
```

## Step 3: Create Artifact Registry
Create a repository to store your Docker images:
```bash
gcloud artifacts repositories create travel-engine-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Repository for Travel Engine images"
```

## Step 4: Build and Push Image
Use **Cloud Build** to build your container and push it to the registry automatically. 
*Note: Run this from the root of your project.*
```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/promptwars-gurgaon/travel-engine-repo/travel-engine:v1 -f src/Dockerfile .
```

## Step 5: Deploy to Cloud Run
Deploy the containerized application. We will inject your API keys as environment variables.

> [!WARNING]
> Replace the values below if you want to use different keys during deployment.

```bash
gcloud run deploy travel-engine \
    --image us-central1-docker.pkg.dev/promptwars-gurgaon/travel-engine-repo/travel-engine:v1 \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_API_KEY=[YOUR_GEMINI_API_KEY]" \
    --set-env-vars="GOOGLE_MAPS_API_KEY=[YOUR_GOOGLE_MAPS_API_KEY]"
```

## Step 6: Verify Deployment
Once the deployment finishes, GCP will provide a URL (e.g., `https://travel-engine-xyz.a.run.app`). 
1. Open the URL in your browser.
2. Interact with the engine to verify AI orchestration and premium UI delivery.

---

## Managing Secrets (Optional but Recommended)
For a production environment, instead of `--set-env-vars`, use **Secret Manager**:
1. Create a secret in GCP Secret Manager.
2. Reference the secret in your Cloud Run deployment using `--set-secrets`.
