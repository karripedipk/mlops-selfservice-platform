.PHONY: help
help:
	@echo "Targets:"
	@echo "  lint            - ruff lint"
	@echo "  format          - ruff format"
	@echo "  test            - pytest"
	@echo "  zip             - create zip artifact (optional)"

lint:
	python -m ruff check .

format:
	python -m ruff format .

test:
	pytest -q
