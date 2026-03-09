#!/bin/bash

# ===========================================
# Hostinger Deployment Script
# ===========================================
# This script deploys the performance fixes to Hostinger
#
# Run this script on your Hostinger server:
# bash deploy-hostinger.sh

set -e  # Exit on error

echo "🚀 Starting Hostinger Deployment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Pull latest changes
echo -e "${YELLOW}📥 Step 1: Pulling latest changes from GitHub...${NC}"
git pull origin main
echo -e "${GREEN}✅ Code updated${NC}"
echo ""

# Step 2: Stop current containers
echo -e "${YELLOW}🛑 Step 2: Stopping current containers...${NC}"
docker compose -f docker-compose.prod.yml down
echo -e "${GREEN}✅ Containers stopped${NC}"
echo ""

# Step 3: Rebuild images
echo -e "${YELLOW}🔨 Step 3: Rebuilding Docker images...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache
echo -e "${GREEN}✅ Images rebuilt${NC}"
echo ""

# Step 4: Start containers
echo -e "${YELLOW}🚀 Step 4: Starting containers...${NC}"
docker compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}✅ Containers started${NC}"
echo ""

# Step 5: Wait for services to be healthy
echo -e "${YELLOW}⏳ Step 5: Waiting for services to be healthy...${NC}"
sleep 10
echo -e "${GREEN}✅ Services should be ready${NC}"
echo ""

# Step 6: Show running containers
echo -e "${YELLOW}📊 Step 6: Checking running services...${NC}"
docker compose -f docker-compose.prod.yml ps
echo ""

# Step 7: Health checks
echo -e "${YELLOW}🏥 Step 7: Running health checks...${NC}"

# Check Redis
echo -n "  - Redis: "
if docker compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check database
echo -n "  - Database: "
if docker compose -f docker-compose.prod.yml exec -T db pg_isready -U poupix > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check Celery worker
echo -n "  - Celery Worker: "
if docker compose -f docker-compose.prod.yml logs celery-worker 2>&1 | grep -q "ready"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  Starting (check logs)${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "  1. Test login at your site"
echo "  2. Upload a file to test Celery processing"
echo "  3. Monitor logs: docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "⚠️  Note: Users will need to re-login once (sessions moved to Redis)"
echo ""

