SRC=$(shell find . -name "*.py"  )

GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null)
GIT_BRANCH_CLEAN := $(shell echo $(GIT_BRANCH) | sed -e "s/[^[:alnum:]]/-/g")
DOCKER_IMAGE := agavecli-dev$(if $(GIT_BRANCH_CLEAN),:$(GIT_BRANCH_CLEAN))

DOCKER_BUILD_ARGS ?= --force-rm
DOCKERFILE ?= Dockerfile

DOCKER_MOUNT := -v "$(CURDIR)":/agavecli
DOCKER_FLAGS := docker run --rm -it $(DOCKER_MOUNT)

DOCKER_RUN_AGAVECLI := $(DOCKER_FLAGS) "$(DOCKER_IMAGE)"

.PHONY: build docs format install shell tests uninstall clean distclean


build: ## Build development container.
	docker build $(DOCKER_BUILD_ARGS) -f "$(DOCKERFILE)" -t "$(DOCKER_IMAGE)" .

docs: ## Generate html from docs.
	pip install sphinx-rtd-theme==0.4.0
	make -C docs/ html

format: $(SRC) ## Format source code.
	yapf -i --style=google $^
	rm -rf pyling.logs
	for py in $(SRC); do \
		echo $${py} >> pyling.logs 2>&1 && \
		pylint --rcfile=rcfile $${py} >> pyling.logs 2>&1; \
	done || exit 0

install: ## Install agavecli system wide.
	pip install -e .

shell: build ## Start a shell inside the build environment.
	$(DOCKER_RUN_AGAVECLI) bash

tests: install 
	pytest -v --cache-clear

uninstall: ## Uninstall agavecli system wide.
	pip uninstall -y agavecli


clean: ## Remove documentation, testing, and runtime artifacts.
	rm -rf docs/_build/
	rm -rf pyling.logs
	rm -rf .cache/
	rm -rf .pytest_cache/
	rm -rf tests/__pycache__/
	rm -rf agavecli.egg-info
	rm -rf agavecli/__pycache__/
	rm -rf agavecli/tenants/__pycache__/
	rm -rf agavecli/clients/__pycache__/
	rm -rf agavecli/auth/__pycache__/
	rm -rf agavecli/systems/__pycache__/
	rm -rf agavecli/utils/__pycache__/
	rm -rf agavecli/files/__pycache__/

distclean: clean uninstall
