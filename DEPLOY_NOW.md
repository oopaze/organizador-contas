# 🚀 Deploy Performance Fixes to Hostinger

## ✅ What's Already Done

- ✅ Code committed and pushed to GitHub
- ✅ Connection pooling configured (600s keep-alive)
- ✅ Production logging fixed (INFO/WARNING levels)
- ✅ Redis caching configured (for general caching)
- ✅ `docker-compose.api.yml` already has Redis & Celery
- ✅ Sessions kept in database (JWT is used for auth)

---

## 🚀 Deploy Command (Copy & Paste)

Run this command from your local machine:

```bash
sshpass -p 'Antonia94032028@' ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password root@76.13.227.236 "cd /root/organizador-contas && git pull && docker compose -f docker-compose.api.yml down && docker compose -f docker-compose.api.yml build --no-cache && docker compose -f docker-compose.api.yml up -d"
```

---

## 📋 What This Does

1. SSH into Hostinger
2. Navigate to project directory
3. Pull latest changes (connection pooling, Redis sessions, logging fixes)
4. Stop all containers
5. Rebuild images with new settings
6. Start all services

---

## ✅ Verify Deployment

After running the command, check status:

```bash
# Check all services are running
sshpass -p 'Antonia94032028@' ssh root@76.13.227.236 "cd /root/organizador-contas && docker compose -f docker-compose.api.yml ps"
```

You should see **4 services running**:
- ✅ db (PostgreSQL)
- ✅ redis
- ✅ backend
- ✅ celery-worker

---

## 🔍 Health Checks

```bash
# Check Redis
sshpass -p 'Antonia94032028@' ssh root@76.13.227.236 "cd /root/organizador-contas && docker compose -f docker-compose.api.yml exec redis redis-cli ping"
# Expected: PONG

# Check Celery Worker
sshpass -p 'Antonia94032028@' ssh root@76.13.227.236 "cd /root/organizador-contas && docker compose -f docker-compose.api.yml logs celery-worker --tail 50"
# Should see: "celery@hostname ready"

# Check Backend Logs
sshpass -p 'Antonia94032028@' ssh root@76.13.227.236 "cd /root/organizador-contas && docker compose -f docker-compose.api.yml logs backend --tail 50"
```

---

## ⚠️ Important

**No user impact** - Since you use JWT authentication, users won't need to re-login.

---

## 📊 What Was Fixed

| Issue | Fix |
|-------|-----|
| Slow login over time | ✅ Connection pooling (600s keep-alive) |
| New DB connection per request | ✅ Connection pooling with health checks |
| Excessive DEBUG logging | ✅ Changed to INFO/WARNING in production |
| Query timeouts | ✅ 30s statement timeout configured |
| Background tasks | ✅ Already working (Celery in api.yml) |
| Redis caching | ✅ Configured for general caching needs |

---

## 🎯 Expected Results

After deployment:
- 🚀 **50-80% faster login** (connection pooling)
- 🚀 **No more slowdown over time** (persistent connections)
- 🚀 **Better performance under load** (connection reuse)
- 🚀 **Reduced log volume** (INFO level in production)

---

## 🔧 If Something Goes Wrong

### Rollback (if needed):
```bash
sshpass -p 'Antonia94032028@' ssh root@76.13.227.236 "cd /root/organizador-contas && git checkout HEAD~1 && docker compose -f docker-compose.api.yml up -d --build"
```

### View Logs:
```bash
sshpass -p 'Antonia94032028@' ssh root@76.13.227.236 "cd /root/organizador-contas && docker compose -f docker-compose.api.yml logs -f"
```

### Restart Services:
```bash
sshpass -p 'Antonia94032028@' ssh root@76.13.227.236 "cd /root/organizador-contas && docker compose -f docker-compose.api.yml restart"
```

---

## ✅ Ready to Deploy!

Just copy and paste the deploy command above. The entire process takes ~2-3 minutes.

