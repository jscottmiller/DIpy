# Build file for DIpy

cover : tests.py dipy.py
	coverage run tests.py
	coverage html
	open htmlcov/dipy.html

test : tests.py dipy.py
	python tests.py

clean :
	rm -rf *.pyc htmlcov .coverage
