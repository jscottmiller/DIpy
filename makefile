# Build file for DIpy

cover : tests.py dipy.py
	coverage run tests.py
	coverage html
	open htmlcov/dipy.html

test : tests.py dipy.py
	python tests.py

readme : README.md
	markdown README.md > readme.html
	open readme.html

clean :
	rm -rf *.pyc htmlcov .coverage *.html
