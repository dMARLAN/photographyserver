.PHONY: format format-diff ruff-check pyright-check unit-tests ci

format:
	../../scripts/format.sh .

format-diff:
	../../scripts/format.sh --diff .

ruff-check:
	uv run ruff check .

pyright-check:
	uv run pyright

unit-tests:
	uv run python -B -m pytest tests/test_config.py tests/test_health.py tests/test_types.py tests/test_watcher.py -v

ci: format-diff ruff-check pyright-check unit-tests
	@echo "Done"
