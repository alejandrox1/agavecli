SRC=$(shell find . -name "*.py"  )

.PHONY: format test install uninstall clean distclean

format: $(SRC)
	yapf -i --style=google $^
	rm -rf pyling.logs
	for py in $(SRC); do \
		echo $${py} >> pyling.logs 2>&1 && \
		pylint --rcfile=rcfile $${py} >> pyling.logs 2>&1; \
	done || exit 0

docs:
	pip install sphinx-rtd-theme==0.4.0
	make -C docs/ html

test:
	pytest -v --cache-clear

install:
	pip install -e .

uninstall:
	pip uninstall -y agavecli


clean:
	make -C docs/ clean
	rm -rf pyling.logs
	rm -rf .cache/
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
