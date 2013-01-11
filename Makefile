docs: pandoc rtd
	pandoc README.md --to rst > docs/source/readme.rst		
	cd docs && make clean && DJANGO_SETTINGS_MODULE=tests.settings make html

publish: docs
	pandoc README.md --to rst > README.rst
	python setup.py sdist
	python setup.py upload
	rm README.rst

.PHONY: docs
