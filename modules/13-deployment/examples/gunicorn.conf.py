# gunicorn.conf.py — Gunicorn configuration file
# Reference: https://docs.gunicorn.org/en/stable/settings.html
#
# Usage:
#   gunicorn myproject.wsgi:application --config gunicorn.conf.py

import multiprocessing

# ── Binding ───────────────────────────────────────────────────────────────────
bind = "0.0.0.0:8000"

# ── Workers ───────────────────────────────────────────────────────────────────
# Rule of thumb: (2 × CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"       # use "gevent" or "uvicorn.workers.UvicornWorker" for async
threads = 2                 # threads per worker (only for gthread worker class)
worker_connections = 1000   # max simultaneous clients (for async workers)

# ── Timeouts ──────────────────────────────────────────────────────────────────
timeout = 120               # seconds before killing an unresponsive worker
keepalive = 5               # seconds to wait for next request on keep-alive connection
graceful_timeout = 30       # seconds to finish in-flight requests on reload/shutdown

# ── Logging ───────────────────────────────────────────────────────────────────
accesslog = "-"             # "-" means stdout (captured by your platform/Docker)
errorlog = "-"              # "-" means stderr
loglevel = "info"           # debug | info | warning | error | critical
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# ── Process naming ────────────────────────────────────────────────────────────
proc_name = "django_app"

# ── Security ─────────────────────────────────────────────────────────────────
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# ── Reload (development only — remove in production) ──────────────────────────
# reload = True
