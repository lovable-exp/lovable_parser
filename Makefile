.PHONY: release bump-version get-version tag push-release install-dev

# Install development dependencies first
install-dev:
	python -m pip install tomli poetry

# Get current version from pyproject.toml
get-version: install-dev
	@python -c 'import tomli; print(tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"])'

# Create a new tag based on current version
tag: install-dev
	$(eval VERSION=$(shell python -c 'import tomli; v=tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"]; print(v)'))
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: Could not determine version"; \
		exit 1; \
	fi
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	@echo "Created tag v$(VERSION)"

# Bump minor version in pyproject.toml
bump-version: install-dev
	$(eval CURRENT_VERSION=$(shell python -c 'import tomli; print(tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"])'))
	@if [ -z "$(CURRENT_VERSION)" ]; then \
		echo "Error: Could not determine current version"; \
		exit 1; \
	fi
	$(eval MAJOR=$(shell echo "$(CURRENT_VERSION)" | cut -d. -f1))
	$(eval MINOR=$(shell echo "$(CURRENT_VERSION)" | cut -d. -f2))
	$(eval NEW_VERSION=$(MAJOR).$(shell expr $(MINOR) + 1).0)
	poetry version $(NEW_VERSION)
	git add pyproject.toml
	git commit -m "chore: bump version to $(NEW_VERSION)"
	@echo "Bumped version to $(NEW_VERSION)"

# Full release process
release: install-dev
	@if [ -n "`git status --porcelain`" ]; then \
		echo "Error: Working directory is not clean. Please commit or stash changes first."; \
		exit 1; \
	fi
	@make tag
	@make bump-version
	git push origin main
	git push origin --tags
	@echo "Release complete! GitHub Actions will handle the PyPI publishing." 