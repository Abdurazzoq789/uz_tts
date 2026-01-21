# Celery Worker Issues - SOLVED ✅

## Problem
```
RuntimeError: Event loop is closed
RuntimeError: Task got Future attached to a different loop
```

## Root Cause
Celery's **prefork pool** (default) forks worker processes. When a process is forked:
1. Parent process has an asyncio event loop
2. Child (forked) process inherits the same loop object
3. But the loop is **dead** in the child process
4. SQLAlchemy async engine tries to use the dead loop → crash

## Solution
Use **solo pool** instead of prefork:
```bash
celery -A tasks worker --pool=solo -Q tts
```

## What Changed
- `celery_config.py`: Added `worker_pool='solo'`
- `start.sh`: Added `--pool=solo` flag

## Solo vs Prefork

| Feature | Prefork (default) | Solo (our fix) |
|---------|------------------|----------------|
| Workers | Multiple processes | Single thread |
| Concurrency | High | Sequential |
| Async support | ❌ Breaks | ✅ Works |
| Best for | CPU tasks | Async I/O tasks |

## Performance Note
Solo pool handles 1 task at a time, but:
- TTS tasks are mostly I/O (model loading, network)
- For production, you can run **multiple solo workers**:
  ```bash
  # 4 solo workers = 4 concurrent jobs (no fork issues)
  celery -A tasks worker --pool=solo -Q tts --concurrency=1 &
  celery -A tasks worker --pool=solo -Q tts --concurrency=1 &
  celery -A tasks worker --pool=solo -Q tts --concurrency=1 &
  celery -A tasks worker --pool=solo -Q tts --concurrency=1 &
  ```

## Alternative: Gevent
For even better async support:
```bash
pip install gevent
celery -A tasks worker --pool=gevent -Q tts --concurrency=10
```

But solo is simpler and works perfectly for this use case.

---

**Status:** ✅ Fixed - Ready to test
