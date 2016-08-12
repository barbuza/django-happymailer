VENV=./venv/

PIP_BIN=${VENV}/bin/pip
PYTHON_BIN=${VENV}/bin/python

NODE_BIN=./node_modules/.bin

all: webpack bdist

dev: webpack
	${PIP_BIN} install -e .

webpack:
	npm run build

bdist:
	${PYTHON_BIN} setup.py bdist --format=gztar

uninstall:
	${PIP_BIN} uninstall django_happymailer

clean:
	rm -rf django_happymailer.egg-info
	rm -rf happymailer/static
	rm -rf {build,dist}