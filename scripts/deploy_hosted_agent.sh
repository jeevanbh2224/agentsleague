#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# The Fractured Orbit — Deploy to Azure Container Registry + Foundry Agent Service
# Usage: ./scripts/deploy_hosted_agent.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

# ── Config — update these ────────────────────────────────────────────────────
ACR_NAME="acrfracturedorbit"           # Azure Container Registry name (must be globally unique)
RESOURCE_GROUP="rg-agents-dev"        # Your resource group
LOCATION="swedencentral"              # Same region as your other resources
IMAGE_NAME="fractured-orbit"
IMAGE_TAG="latest"

# ── Derived ──────────────────────────────────────────────────────────────────
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
FULL_IMAGE="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "  THE FRACTURED ORBIT — HOSTED AGENT DEPLOYMENT"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Create ACR if it doesn't exist
echo "  [1/5] Creating Azure Container Registry..."
az acr create \
  --name "$ACR_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --sku Basic \
  --admin-enabled true \
  2>/dev/null || echo "  ACR already exists, skipping."

# Step 2: (no local Docker login needed — ACR cloud build handles auth)
echo "  [2/5] Skipping local Docker login (using ACR cloud build)..."

# Step 3: Build AND push using ACR Tasks — no Docker Desktop required
echo "  [3/5] Building image in Azure (az acr build)..."
cd "$(dirname "$0")/.."
az acr build \
  --registry "$ACR_NAME" \
  --image "${IMAGE_NAME}:${IMAGE_TAG}" \
  --platform linux/amd64 \
  .

echo "  [4/5] Image built and pushed by ACR (no local push needed)..."

# Step 4: Print next steps for Foundry Agent Service
echo ""
echo "  [5/5] Image pushed successfully!"
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NEXT: Register as Hosted Agent in Foundry"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Image: ${FULL_IMAGE}"
echo ""
echo "  1. Go to https://ai.azure.com → your project → Agents"
echo "  2. Create a new Hosted Agent"
echo "  3. Container image: ${FULL_IMAGE}"
echo "  4. Port: 8080"
echo "  5. Add environment variables from your .env file"
echo "  6. Health check path: /health"
echo ""
echo "  API Endpoints once deployed:"
echo "    POST  /sessions              — start new game"
echo "    POST  /sessions/{id}/turn    — take a turn"
echo "    GET   /sessions/{id}         — get state"
echo "    GET   /health                — health check"
echo ""
