docs: 
	pandoc README.md --to rst > docs/source/readme.rst		
	pandoc README.md --to rst > README.rst
	cd docs && make clean && make html

publish: docs
	python setup.py sdist upload

.PHONY: docs
