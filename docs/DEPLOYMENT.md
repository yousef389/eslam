# ============================================
# Sanitary ERP - Deployment Guide
# ============================================

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Database Backup](#database-backup)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores

### Required Software
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install other utilities
sudo apt update
sudo apt install -y git curl wget openssl
```

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sanitary-erp.git
cd sanitary-erp
```

### 2. Run Setup
```bash
# Make scripts executable
chmod +x docker/scripts/*.sh

# Run setup
make setup
# or
./docker/scripts/deploy.sh setup
```

### 3. Configure Environment
```bash
# Edit the .env file with your settings
nano .env
```

**Important variables to change:**
- `JWT_SECRET_KEY` - Generate with: `openssl rand -base64 48`
- `DB_PASSWORD` - Use a strong password
- `REDIS_PASSWORD` - Use a strong password
- `CORS_ORIGINS` - Your domain(s)
- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `OPENAI_API_KEY` - From OpenAI
- `AI_GEMINI_API_KEY` - From Google AI Studio

### 4. Start Services
```bash
make start
# or
./docker/scripts/deploy.sh start
```

### 5. Verify Installation
```bash
make health
# or
curl http://localhost/health
```

---

## Manual Installation

### Step 1: Create Environment File
```bash
cp .env.production .env
nano .env
```

### Step 2: Build and Start Services
```bash
# Build images
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps
```

### Step 3: Initialize Database
```bash
# Run migrations
docker compose exec api alembic upgrade head

# Seed initial data
docker compose exec api python scripts/seed_data.py
```

### Step 4: Create Admin User
```bash
docker compose exec api python scripts/create_admin.py
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Sanitary ERP |
| `DEBUG` | Debug mode | false |
| `ENVIRONMENT` | Environment | production |
| `DB_USER` | Database user | erp_production_user |
| `DB_PASSWORD` | Database password | - |
| `DB_NAME` | Database name | sanitary_erp_production |
| `JWT_SECRET_KEY` | JWT secret | - |
| `REDIS_PASSWORD` | Redis password | - |
| `CORS_ORIGINS` | Allowed origins | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `AI_GEMINI_API_KEY` | Gemini API key | - |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | - |

### Generate Secure Secrets
```bash
# Generate JWT secret
openssl rand -base64 48

# Generate Redis password
openssl rand -base64 24

# Generate Grafana password
openssl rand -base64 16
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install -y certbot

# Stop nginx temporarily
docker compose stop nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/

# Update nginx.conf (uncomment HTTPS server block)

# Start nginx
docker compose start nginx

# Setup auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet && docker compose restart nginx
```

### Option 2: Self-Signed Certificate
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout docker/nginx/ssl/privkey.pem \
    -out docker/nginx/ssl/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

---

## Database Backup

### Automated Backups
```bash
# Create backup
make backup

# Or manually
docker compose exec postgres /docker-entrypoint-initdb.d/backup.sh
```

### Schedule Daily Backups (Cron)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/sanitary-erp && make backup >> /var/log/erp-backup.log 2>&1
```

### Restore from Backup
```bash
# List backups
ls -lh /backups/postgres/

# Restore specific backup
./docker/scripts/deploy.sh restore /backups/postgres/sanitary_erp_production_20240101_020000.sql.gz
```

### Backup Location
- Backups are stored in: `/backups/postgres/`
- Retention: 30 days (configurable in backup.sh)

---

## Monitoring

### Prometheus
- URL: http://localhost:9090 (internal only)
- Metrics endpoint: http://api:8000/metrics

### Grafana
- URL: http://localhost:3001
- Default credentials: admin / (password from .env)

### Service Status
```bash
# Check all services
make status

# Check specific service
docker compose ps api

# View logs
make logs
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
sudo lsof -i :80
sudo lsof -i :443

# Kill process
sudo kill -9 <PID>
```

#### 2. Database Connection Error
```bash
# Check PostgreSQL status
docker compose ps postgres

# View logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres
```

#### 3. Redis Connection Error
```bash
# Check Redis status
docker compose ps redis

# Test connection
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} ping
```

#### 4. API Not Responding
```bash
# Check API logs
docker compose logs api

# Restart API
docker compose restart api

# Check health
curl http://localhost/health
```

#### 5. Permission Denied
```bash
# Fix upload permissions
sudo chown -R 1001:1001 uploads/

# Fix script permissions
chmod +x docker/scripts/*.sh
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api
```

### Reset Everything
```bash
# Stop and remove all data
docker compose down -v

# Remove images
docker compose down --rmi all

# Start fresh
make setup
make start
```

---

## Support

For issues and questions:
- GitHub: https://github.com/yourusername/sanitary-erp/issues
- Documentation: https://yourdomain.com/docs
