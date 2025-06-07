DOCKER_COMPOSE_CMD := "./docker_compose/docker-compose.sh"

.PHONY: build up up-dev validate-api validate-db validate-frontend ci


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

ci: validate-api validate-db validate-frontend
	@echo "Done"
