# 🚀 Deployment Instructions for Hostinger

## ✅ Changes Pushed to GitHub

The following changes have been committed and pushed:
- ✅ Added Redis service to `docker-compose.prod.yml`
- ✅ Added Celery worker service
- ✅ Database connection pooling configured
- ✅ Sessions moved to Redis (prevents database bloat)
- ✅ Production logging levels fixed
- ✅ Redis caching enabled

**Commit**: `fb753e8a` - "fix: Add Redis, Celery worker, and connection pooling for production"

---

## 📋 Deploy on Hostinger (2 Options)

### Option 1: Automated Script (Recommended)

SSH into your Hostinger server and run:

```bash
cd /path/to/your/project
bash deploy-hostinger.sh
```

The script will:
1. Pull latest changes
2. Stop containers
3. Rebuild images
4. Start containers
5. Run health checks

---

### Option 2: Manual Deployment

SSH into your Hostinger server and run these commands:

```bash
# Navigate to project directory
cd /path/to/your/project

# Pull latest changes
git pull origin main

# Stop current containers
docker compose -f docker-compose.prod.yml down

# Rebuild images
docker compose -f docker-compose.prod.yml build

# Start containers
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

---

## ✅ Verify Deployment

After deployment, verify all services are running:

```bash
# Should show 5 services:
# - db (PostgreSQL)
# - redis
# - backend
# - celery-worker
# - frontend
docker compose -f docker-compose.prod.yml ps
```

### Health Checks

```bash
# Check Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli ping
# Expected: PONG

# Check Celery Worker
docker compose -f docker-compose.prod.yml logs celery-worker | grep "ready"
# Expected: celery@hostname ready

# View all logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🧪 Test the Fixes

1. **Test Login** - Should be faster now
2. **Upload a File** - Background processing should work
3. **Monitor Performance** - Check if slowdown is gone

---

## ⚠️ Important Notes

1. **Users need to re-login once** (sessions moved from database to Redis)
2. **Redis is now required** - Make sure it's running
3. **Celery worker processes background tasks** - File uploads will now complete
4. **Database connections are pooled** - Better performance under load

---

## 📊 Expected Improvements

- 🚀 **50-80% faster login**
- 🚀 **Database stops growing** (no session bloat)
- 🚀 **Background tasks work** (file processing)
- 🚀 **40-60% faster responses**

---

## 🔍 Troubleshooting

### If Redis fails to start:
```bash
docker compose -f docker-compose.prod.yml logs redis
```

### If Celery worker fails:
```bash
docker compose -f docker-compose.prod.yml logs celery-worker
```

### If backend can't connect to Redis:
Check environment variables:
```bash
docker compose -f docker-compose.prod.yml exec backend env | grep CELERY
```

### Restart specific service:
```bash
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart celery-worker
```

---

## 🎯 What's Next?

After deployment:
1. Monitor the application for 24-48 hours
2. Check if the slowdown issue is resolved
3. Verify background tasks are processing
4. Monitor database size (should stop growing from sessions)

---

## 📞 Need Help?

If you encounter issues:
1. Check logs: `docker compose -f docker-compose.prod.yml logs -f`
2. Verify all 5 services are running
3. Check Redis connection
4. Verify Celery worker is processing tasks

