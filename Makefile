clean:
	rm -rf build dist *.egg-info
	rm -rf venv/Lib/site-packages/jsonnet_binary-*

install: clean
	pip install .
