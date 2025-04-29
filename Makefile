.PHONY: release bump-version get-version tag push-release

# Get current version from pyproject.toml
get-version:
	@python -c 'import tomli; print(tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"])'

# Create a new tag based on current version
tag:
	$(eval VERSION=$(shell python -c 'import tomli; print(tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"])'))
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	@echo "Created tag v$(VERSION)"

# Bump minor version in pyproject.toml
bump-version:
	$(eval CURRENT_VERSION=$(shell python -c 'import tomli; print(tomli.load(open("pyproject.toml", "rb"))["tool"]["poetry"]["version"])'))
	$(eval MAJOR=$(shell echo $(CURRENT_VERSION) | cut -d. -f1))
	$(eval MINOR=$(shell echo $(CURRENT_VERSION) | cut -d. -f2))
	$(eval PATCH=$(shell echo $(CURRENT_VERSION) | cut -d. -f3))
	$(eval NEW_VERSION=$(MAJOR).$(shell expr $(MINOR) + 1).0)
	@poetry version $(NEW_VERSION)
	git add pyproject.toml
	git commit -m "chore: bump version to $(NEW_VERSION)"
	@echo "Bumped version to $(NEW_VERSION)"

# Full release process
release:
	@if [ -n "`git status --porcelain`" ]; then \
		echo "Error: Working directory is not clean. Please commit or stash changes first."; \
		exit 1; \
	fi
	@make tag
	@make bump-version
	git push origin main
	git push origin --tags
	@echo "Release complete! GitHub Actions will handle the PyPI publishing."

# Install development dependencies
install-dev:
	pip install tomli poetry 