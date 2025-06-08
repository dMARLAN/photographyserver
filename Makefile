DOCKER_COMPOSE_CMD := "./docker_compose/docker-compose.sh"

.PHONY: build up up-dev down \
validate-api validate-db validate-sync validate-frontend \
format-api format-api-diff format-db format-db-diff format-sync format-sync-diff format-all format-all-diff \
ci


### Docker Compose targets
build:
	$(DOCKER_COMPOSE_CMD) build

up: build
	$(DOCKER_COMPOSE_CMD) up

up-dev: build
	$(DOCKER_COMPOSE_CMD) up --watch

down:
	$(DOCKER_COMPOSE_CMD) down


### Validation targets
validate-api:
	@echo "### Validating API..."
	cd src/pgs_api && uv run make ci
	@echo "### API validation completed successfully\n"

validate-db:
	@echo "### Validating Database..."
	cd src/pgs_db && uv run make ci
	@echo "### Database validation completed successfully\n"

validate-sync:
	@echo "### Validating Sync Worker..."
	cd src/pgs_sync && uv run make ci
	@echo "### Sync Worker validation completed successfully\n"

validate-frontend:
	@echo "### Validating Frontend..."
	cd src/frontend && npm run lint
	@echo "### Frontend validation completed successfully\n"


### Formatting targets
format-api:
	cd src/pgs_api && uv run make format

format-api-diff:
	cd src/pgs_api && uv run make format-diff

format-db:
	cd src/pgs_db && uv run make format

format-db-diff:
	cd src/pgs_db && uv run make format-diff

format-sync:
	cd src/pgs_sync && uv run make format

format-sync-diff:
	cd src/pgs_sync && uv run make format-diff

format-all: format-api format-db format-sync
	@echo "All code formatted successfully"

format-all-diff: format-api-diff format-db-diff format-sync-diff
	@echo "All code formatting checked"


### Continuous Integration target
ci: validate-api validate-db validate-sync validate-frontend format-all-diff
	@echo "Done"
