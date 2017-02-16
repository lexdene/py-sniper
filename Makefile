unit-test:
	python -m unittest discover -v tests/ 'test_*.py'

flake8:
	flake8 sniper/ tests/ examples/

check-isort:
	isort --check-only --recursive sniper/ tests/ examples/

test: unit-test flake8 check-isort
