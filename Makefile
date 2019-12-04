MODULE            = registrable
INTEGRATION_TESTS = tests
SRC              := $(MODULE) $(INTEGRATION_TESTS)
PYTEST_COMMAND    = python -m pytest -v --color=yes
PYTHONPATH        = $(INTEGRATION_TESTS)
VERSION           = $(shell python -c 'from registrable.version import VERSION; print(VERSION)')

.PHONY : clean
clean :
	@find . \
		| grep -E "(__pycache__|\.mypy_cache|\.pytest_cache|\.pyc|\.pyo$$)" \
		| xargs rm -rf
	@rm -rf build/
	@rm -rf dist/
	@rm -rf $(PROJECT)

.PHONY : version
version :
	@echo $(VERSION)

.PHONY : typecheck
typecheck :
	@echo "Typechecks: mypy"
	@PYTHONPATH=$(PYTHONPATH) python -m mypy $(SRC) --ignore-missing-imports --no-site-packages

.PHONY : lint
lint :
	@echo "Lint: flake8"
	@PYTHONPATH=$(PYTHONPATH) python -m flake8 $(SRC)
	@echo "Lint: black"
	@PYTHONPATH=$(PYTHONPATH) python -m black --check $(SRC)

.PHONY : unit-tests
unit-tests :
	@echo "Unit tests: pytest"
	@PYTHONPATH=$(PYTHONPATH) $(PYTEST_COMMAND) $(MODULE)

.PHONY : integration-tests
integration-tests :
	@echo "Integration tests: pytest"
	@PYTHONPATH=$(PYTHONPATH) $(PYTEST_COMMAND) $(INTEGRATION_TESTS)

.PHONY : test
test : typecheck lint unit-tests integration-tests

.PHONY : docs
docs :
	cd docs && make html

.PHONY: create-branch
create-branch :
ifneq ($(issue),)
	git checkout -b ISSUE-$(issue)
	git push --set-upstream origin ISSUE-$(issue)
else ifneq ($(name),)
	git checkout -b $(name)
	git push --set-upstream origin $(name)
else
	$(error must supply 'issue' or 'name' parameter)
endif

.PHONY : delete-branch
delete-branch :
	@BRANCH=`git rev-parse --abbrev-ref HEAD` \
		&& [ $$BRANCH != 'master' ] \
		&& echo "On branch $$BRANCH" \
		&& echo "Checking out master" \
		&& git checkout master \
		&& git pull \
		&& echo "Deleting branch $$BRANCH" \
		&& git branch -d $$BRANCH \
		&& git remote prune origin

.PHONY : install
install :
	python setup.py develop

.PHONY : uninstall
uninstall :
	@rm -rf ./$(MODULE).egg-info/
	@python setup.py develop --uninstall

.PHONY : release
release :
	git add -A
	git commit -m "Release: $(VERSION)"
	git tag $(VERSION) -m "Adds tag $(VERSION) for PyPI"
	git push --tags origin master

.PHONY : build
build :
	@echo "Building package wheel distribution"
	@python setup.py bdist_wheel
	@echo "Building package source distribution"
	@python setup.py sdist

.PHONY : check-upload
check-upload :
	@twine upload dist/* -r pypitest
	@echo "Go to https://test.pypi.org/project/registrable/ to verify"

.PHONY : upload
upload :
	@twine upload dist/* -r pypi
