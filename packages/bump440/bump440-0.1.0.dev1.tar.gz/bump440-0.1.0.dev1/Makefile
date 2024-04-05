.PHONY: help ensure-clean ensure-dev-branch requirements dev-requirements pre-commit
.DEFAULT_GOAL := help
SHELL = sh -s

# -- global targets --
## This help screen
help:
	@echo "Available targets:"
	@awk '/^[a-zA-Z\-\_0-9%:\\ ]+/ { \
	  helpMessage = match(lastLine, /^## (.*)/); \
	  if (helpMessage) { \
	    helpCommand = $$1; \
	    helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
	    gsub("\\\\", "", helpCommand); \
	    gsub(":+$$", "", helpCommand); \
	    printf "  \x1b[32;01m%-35s\x1b[0m %s\n", helpCommand, helpMessage; \
	  } \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort -u

# Check for uncommitted changes
ensure-clean:
	@if ! git diff-index --quiet HEAD -- || ! git diff --staged --quiet; then \
		echo "Uncommitted or unstaged changes found. Please commit and stage your changes."; \
		exit 1; \
	fi

# Check if current branch is dev
ensure-dev-branch:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "dev" ]; then \
		echo "Current branch is not dev. Please switch to the dev branch."; \
		exit 1; \
	fi

# -- Dependencies --
## Make requirements
requirements:
	@echo "Pip-compile requirements"
	@python -m piptools compile --strip-extras requirements.in

## Make development requirements
dev-requirements:
	@echo "Pip-compile dev-requirements"
	@python -m piptools compile  --strip-extras dev-requirements.in

# -- Git and Commit --
## Run pre-commit
pre-commit:
	@echo "Running pre-commit"
	@pre-commit run --all-files


# -- Development --
## Install Locally for Development
install:
	@echo "Uninstalling old version:"
	@pip uninstall -y bump440
	@echo "Installing locally for development"
	@flit install --symlink


## Publish the package to PyPi
publish:
	@echo "Publishing the package to PyPi"
	@flit publish
