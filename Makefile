.PHONY: help setup start stop restart logs status backup restore update health

# Default target
help:
	@echo "Sanitary ERP - Deployment Commands"
	@echo "=================================="
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  setup     - Initial project setup"
	@echo "  start     - Start all services"
	@echo "  stop      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - View service logs"
	@echo "  status    - Check service status"
	@echo "  backup    - Create database backup"
	@echo "  update    - Update and rebuild services"
	@echo "  health    - Check service health"
	@echo "  dev       - Start in development mode"
	@echo "  prod      - Start in production mode"
	@echo ""

# Setup
setup:
	@./docker/scripts/deploy.sh setup

# Start services
start:
	@./docker/scripts/deploy.sh start

# Stop services
stop:
	@./docker/scripts/deploy.sh stop

# Restart services
restart:
	@./docker/scripts/deploy.sh restart

# View logs
logs:
	@./docker/scripts/deploy.sh logs

# Check status
status:
	@./docker/scripts/deploy.sh status

# Backup database
backup:
	@./docker/scripts/deploy.sh backup

# Update services
update:
	@./docker/scripts/deploy.sh update

# Health check
health:
	@./docker/scripts/deploy.sh health

# Development mode
dev:
	docker compose -f docker-compose.dev.yml up -d

# Production mode
prod:
	docker compose up -d --build

# Clean all data (DANGER!)
clean:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " [ "$$REPLY" = "y" ] || exit 1
	docker compose down -v
	rm -rf uploads/*

# Generate secrets
secrets:
	@echo "JWT_SECRET_KEY=$$(openssl rand -base64 48)"
	@echo "REDIS_PASSWORD=$$(openssl rand -base64 24)"
	@echo "GRAFANA_PASSWORD=$$(openssl rand -base64 16)"
