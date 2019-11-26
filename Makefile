MODULE            = registrable
SRC              := $(MODULE)
PYTEST_COMMAND    = python -m pytest -v --color=yes

.PHONY : clean
clean :
	@find . \
		| grep -E "(__pycache__|\.mypy_cache|\.pytest_cache|\.pyc|\.pyo$$)" \
		| xargs rm -rf
	@rm -rf $(PROJECT)

.PHONY : typecheck
typecheck :
	@echo "Typechecks: mypy"
	@python -m mypy $(SRC) --ignore-missing-imports --no-site-packages

.PHONY : lint
lint :
	@echo "Lint: flake8"
	@python -m flake8 $(SRC)
	@echo "Lint: black"
	@python -m black --check $(SRC)

.PHONY : unit-tests
unit-tests :
	@echo "Unit tests: pytest"
	@$(PYTEST_COMMAND) $(SRC)

.PHONY : test
test : typecheck lint unit-tests

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
