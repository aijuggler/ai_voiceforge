# ---------- Project settings ----------
PROJECT_NAME := ai_voiceforge   # docker compose project name

# Detect the compose file (prefer compose.yml, fall back to docker-compose.yml)
ifdef COMPOSE_FILE                      # allow override: make COMPOSE_FILE=myfile.yml up
  _COMPOSE_FILE := $(COMPOSE_FILE)
else ifneq ($(wildcard compose.yml),)
  _COMPOSE_FILE := compose.yml
else
  _COMPOSE_FILE := docker-compose.yml
endif

# Compose command (v2 CLI)
DC := docker compose -p $(PROJECT_NAME) -f $(_COMPOSE_FILE)

# Default goal: build images AND start containers
.DEFAULT_GOAL := all

# ---------- Phony targets ----------
.PHONY: all build up down restart reload-backend reload-frontend reload \
        clean logs ps shell-backend shell-frontend run_server

# Build _and_ bring everything up when you just type `make`
all: build up

# Build images only
build:
	$(DC) build

# Start (or attach to) containers in detached mode
up:
	$(DC) up -d

# Stop and remove containers, keeping volumes
down:
	$(DC) down

# Full restart: stop then start
restart:
	$(DC) down
	$(DC) up -d

# Rebuild & restart just the backend container
reload-backend:
	$(DC) up -d --build --force-recreate backend

# Rebuild & restart just the frontend container
reload-frontend:
	$(DC) up -d --build --force-recreate frontend

# Rebuild & restart both backend and frontend
reload: reload-backend reload-frontend

# Remove project containers, networks, and volumes; prune dangling Docker objects
clean:
	$(DC) down -v --remove-orphans
	docker container prune -f
	docker image prune -f

# Tail logs from all services
logs:
	$(DC) logs -f

logs-backend:
	$(DC) logs -f backend

logs-frontend:
	$(DC) logs -f frontend


# Show container status (including exited)
ps:
	$(DC) ps -a

# Open an interactive shell inside running containers
shell-backend:
	$(DC) exec backend /bin/sh

shell-frontend:
	$(DC) exec frontend /bin/sh

# Run the server (start both services, open frontend, show backend logs)
run_server:
	$(DC) up -d --build
	open http://localhost:3000
	$(DC) logs -f backend