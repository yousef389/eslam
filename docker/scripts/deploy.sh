#!/bin/bash

# ============================================
# Deployment Script
# ============================================
# Usage: ./deploy.sh [command]
# Commands: setup, start, stop, restart, logs, backup, restore, update

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

# Functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check .env file
    if [ ! -f .env ]; then
        log_warn ".env file not found. Creating from .env.production..."
        cp .env.production .env
        log_warn "Please edit .env with your configuration before starting"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

setup() {
    log_info "Setting up the project..."
    
    # Create necessary directories
    mkdir -p docker/nginx/ssl
    mkdir -p docker/prometheus
    mkdir -p uploads/telegram uploads/ai/temp
    
    # Generate JWT secret if not set
    if grep -q "CHANGE_ME_GENERATE_RANDOM_64_CHARS" .env; then
        JWT_SECRET=$(openssl rand -base64 48)
        sed -i "s/CHANGE_ME_GENERATE_RANDOM_64_CHARS/${JWT_SECRET}/" .env
        log_info "Generated JWT secret"
    fi
    
    # Generate Redis password if not set
    if grep -q "redis_password_123" .env; then
        REDIS_PASS=$(openssl rand -base64 24)
        sed -i "s/redis_password_123/${REDIS_PASS}/" .env
        log_info "Generated Redis password"
    fi
    
    log_info "Setup completed"
    log_info "Please edit .env file with your configuration"
}

start() {
    log_info "Starting services..."
    docker compose up -d
    log_info "Services started. Use 'docker compose ps' to check status"
}

stop() {
    log_info "Stopping services..."
    docker compose down
    log_info "Services stopped"
}

restart() {
    log_info "Restarting services..."
    docker compose restart
    log_info "Services restarted"
}

logs() {
    docker compose logs -f --tail=100
}

status() {
    docker compose ps
}

backup() {
    log_info "Creating database backup..."
    docker compose exec postgres /docker-entrypoint-initdb.d/backup.sh
    log_info "Backup completed"
}

restore() {
    if [ -z "${1:-}" ]; then
        log_error "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    if [ ! -f "${BACKUP_FILE}" ]; then
        log_error "Backup file not found: ${BACKUP_FILE}"
        exit 1
    fi
    
    log_warn "This will overwrite the current database!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    log_info "Restoring from backup: ${BACKUP_FILE}"
    gunzip -c "${BACKUP_FILE}" | docker compose exec -T postgres psql -U "${DB_USER:-erp_production_user}" -d "${DB_NAME:-sanitary_erp_production}"
    log_info "Restore completed"
}

update() {
    log_info "Updating services..."
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    log_info "Update completed"
}

health() {
    log_info "Checking service health..."
    
    # Check API
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        log_info "API: Healthy"
    else
        log_error "API: Unhealthy"
    fi
    
    # Check PostgreSQL
    if docker compose exec postgres pg_isready -U "${DB_USER:-erp_production_user}" > /dev/null 2>&1; then
        log_info "PostgreSQL: Healthy"
    else
        log_error "PostgreSQL: Unhealthy"
    fi
    
    # Check Redis
    if docker compose exec redis redis-cli ping > /dev/null 2>&1; then
        log_info "Redis: Healthy"
    else
        log_error "Redis: Unhealthy"
    fi
}

# Main
case "${1:-help}" in
    setup)
        check_prerequisites
        setup
        ;;
    start)
        check_prerequisites
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    backup)
        backup
        ;;
    restore)
        restore "${2:-}"
        ;;
    update)
        update
        ;;
    health)
        health
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|logs|status|backup|restore|update|health}"
        echo ""
        echo "Commands:"
        echo "  setup    - Initial project setup"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - View service logs"
        echo "  status   - Check service status"
        echo "  backup   - Create database backup"
        echo "  restore  - Restore from backup"
        echo "  update   - Update and rebuild services"
        echo "  health   - Check service health"
        ;;
esac
