.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@poetry env info
	

.PHONY: install
install:          ## Install the project in dev mode.
	@poetry install

.PHONY: run
run:          ## Install the project in dev mode.
	@poetry run image_quality_sampler

.PHONY: fmt
fmt:              ## Format code using black & isort.
	poetry run isort image_quality_sampler/
	poetry run black -l 79 image_quality_sampler/
	poetry run black -l 79 tests/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	poetry run flake8 image_quality_sampler/
	poetry run black -l 79 --check image_quality_sampler/
	poetry run black -l 79 --check tests/
	poetry run mypy --ignore-missing-imports image_quality_sampler/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	poetry run pytest -v --cov-config .coveragerc --cov=image_quality_sampler -l --tb=short --maxfail=1 tests/
	poetry run coverage xml
	poetry run coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr poetry run pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
ifeq ($(OS),Windows_NT)
	@clean.bat
else
	@./clean.sh
endif

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	@poetry shell

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create s version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver) : " TAG; \
	poetry run gitchangelog > HISTORY.md; \
	git add image_quality_sampler/VERSION HISTORY.md; \
	git commit -m "release: version ${TAG} 🚀"; \
	echo "creating git tag : ${TAG}"; \
	git tag ${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@poetry run mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL

.PHONY: package
package:		## Create new executable for windows systems
	@echo "Packaging up application..."
	@poetry run pyinstaller --name "AMS Capture - Quality Control Module" --windowed --add-data ".\image_quality_sampler\resources\;resources" .\image_quality_sampler\__main__.py
	@echo "Application packaged. Check dist folder."