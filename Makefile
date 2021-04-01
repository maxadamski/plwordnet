.PHONY: clean build publish

clean:
	rm -r build/ dist/ *.egg-info/

build:
	python setup.py sdist
	python setup.py bdist_wheel --universal

publish:
	twine check dist/* && twine upload dist/*
