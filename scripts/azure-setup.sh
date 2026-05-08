#!/bin/bash
# scripts/azure-setup.sh
# Azure Container Apps 一键部署脚本 / One-click deployment script

set -euo pipefail

# ====== 配置变量 / Configuration ======
RESOURCE_GROUP="rg-smart-room-booking"
LOCATION="eastasia"
ENVIRONMENT_NAME="cae-smart-room-booking"
APP_NAME="ca-smart-room-booking"
GITHUB_REPO="<YOUR_GITHUB_USERNAME>/smart-room-booking"
IMAGE="ghcr.io/${GITHUB_REPO}:latest"

echo "🔧 Step 1: 创建资源组 / Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

echo "🔧 Step 2: 创建 Container Apps 环境 / Creating Container Apps environment..."
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

echo "🔧 Step 3: 创建 Container App / Creating Container App..."
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $IMAGE \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    "ENVIRONMENT=production" \
    "JWT_SECRET=secretref:jwt-secret" \
    "DATABASE_URL=sqlite:///./data/booking.db" \
  --registry-server ghcr.io \
  --registry-username $GITHUB_REPO \
  --registry-password "<GITHUB_PAT>"

echo "🔧 Step 4: 配置健康检查探针 / Configuring health probes..."
az containerapp update \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "ENVIRONMENT=production" \
  --yaml - <<YAML
properties:
  template:
    containers:
      - name: $APP_NAME
        probes:
          - type: Liveness
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          - type: Readiness
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          - type: Startup
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 5
            failureThreshold: 30
YAML

echo "🔧 Step 5: 配置 GitHub OIDC / Setting up GitHub OIDC..."
# 创建 Azure AD App Registration / Create Azure AD App Registration
APP_REG=$(az ad app create --display-name "github-deploy-smart-room-booking" --query appId -o tsv)
SP_ID=$(az ad sp create --id $APP_REG --query id -o tsv)

# 分配权限 / Assign permissions
az role assignment create \
  --assignee $SP_ID \
  --role "Contributor" \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP"

# 创建联合凭据 / Create federated credential
az ad app federated-credential create \
  --id $APP_REG \
  --parameters "{
    \"name\": \"github-main-branch\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"repo:${GITHUB_REPO}:ref:refs/heads/main\",
    \"audiences\": [\"api://AzureADTokenExchange\"]
  }"

# 获取部署所需信息 / Get deployment info
FQDN=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

TENANT_ID=$(az account show --query tenantId -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

echo ""
echo "======================================================"
echo "✅ 部署完成！/ Deployment complete!"
echo "======================================================"
echo ""
echo "🌐 应用 URL / App URL: https://$FQDN"
echo ""
echo "📋 请在 GitHub 仓库 Settings → Secrets 中配置以下值："
echo "   Please configure these in GitHub repo Settings → Secrets:"
echo ""
echo "   AZURE_CLIENT_ID     = $APP_REG"
echo "   AZURE_TENANT_ID     = $TENANT_ID"
echo "   AZURE_SUBSCRIPTION_ID = $SUBSCRIPTION_ID"
echo ""
echo "🔗 健康检查 / Health check: https://$FQDN/api/v1/health"
echo "======================================================"
