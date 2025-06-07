DOCKER_COMPOSE_CMD := "./docker_compose/docker-compose.sh"

.PHONY: build up up-dev down \
validate-api validate-db validate-frontend \
format-api format-api-diff format-db format-db-diff format-all format-all-diff \
ci


### Docker Compose targets
build:
	$(DOCKER_COMPOSE_CMD) build

up:
	$(DOCKER_COMPOSE_CMD) up

up-dev:
	$(DOCKER_COMPOSE_CMD) up --watch

down:
	$(DOCKER_COMPOSE_CMD) down


### Validation targets
validate-api:
	cd src/pgs_api && uv run make ci

validate-db:
	cd src/pgs_db && uv run make ci

validate-frontend:
	cd src/frontend && npm run lint


### Formatting targets
format-api:
	cd src/pgs_api && uv run make format

format-api-diff:
	cd src/pgs_api && uv run make format-diff

format-db:
	cd src/pgs_db && uv run make format

format-db-diff:
	cd src/pgs_db && uv run make format-diff

format-all: format-api format-db
	@echo "All code formatted successfully"

format-all-diff: format-api-diff format-db-diff
	@echo "All code formatting checked"


### Continuous Integration target
ci: validate-api validate-db validate-frontend format-all-diff
	@echo "Done"
