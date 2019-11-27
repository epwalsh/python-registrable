MODULE            = registrable
INTEGRATION_TESTS = tests
SRC              := $(MODULE) $(INTEGRATION_TESTS)
PYTEST_COMMAND    = python -m pytest -v --color=yes
PYTHONPATH        = $(INTEGRATION_TESTS)

.PHONY : clean
clean :
	@find . \
		| grep -E "(__pycache__|\.mypy_cache|\.pytest_cache|\.pyc|\.pyo$$)" \
		| xargs rm -rf
	@rm -rf $(PROJECT)

.PHONY : version
version :
	@python -c 'from registrable.version import VERSION; print(VERSION)'

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

.PHONY : install
install :
	python setup.py develop

.PHONY : uninstall
uninstall :
	@rm -rf ./$(MODULE).egg-info/
	@python setup.py develop --uninstall

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
