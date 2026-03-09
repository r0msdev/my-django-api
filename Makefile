.DEFAULT_GOAL := help
PYTHON        := .venv/bin/python
MANAGE        := $(PYTHON) djangoapi/manage.py

# ── Help ──────────────────────────────────────────────────────────────────────

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Environment ───────────────────────────────────────────────────────────────

.PHONY: install
install: ## Install dev dependencies into .venv
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements/dev.txt

.PHONY: install-prod
install-prod: ## Install prod dependencies into .venv
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements/prod.txt

# ── Lint ──────────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Run pylint over the project
	.venv/bin/pylint djangoapi

# ── Tests ─────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run all tests
	$(MANAGE) test core apps --verbosity=2

.PHONY: test-fast
test-fast: ## Run all tests (minimal output)
	$(MANAGE) test core apps

# ── Database ──────────────────────────────────────────────────────────────────

.PHONY: migrate
migrate: ## Apply migrations
	$(MANAGE) migrate

.PHONY: migrations
migrations: ## Create new migrations
	$(MANAGE) makemigrations

# ── Dev server ────────────────────────────────────────────────────────────────

.PHONY: run
run: ## Start Django dev server locally
	$(MANAGE) runserver

.PHONY: check
check: ## Run Django system checks
	$(MANAGE) check

# ── Docker ────────────────────────────────────────────────────────────────────

.PHONY: docker-dev
docker-dev: ## Build and run dev container
	docker compose --profile dev up --build

.PHONY: docker-prod
docker-prod: ## Build and run prod container
	docker compose --profile prod up --build

.PHONY: docker-down
docker-down: ## Stop all containers
	docker compose down

# ── Combined ──────────────────────────────────────────────────────────────────

.PHONY: ci
ci: check lint test ## Run all checks (system check + lint + tests)
