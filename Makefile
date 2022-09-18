.PHONY: fmt
fmt:
	black .
	isort . --profile black
	autoflake --in-place --remove-all-unused-imports --recursive .

.PHONY: lint
lint:
	black --check .
	isort --profile black --check .
	flake8 .

.PHONY: devserver
devserver:
	sh ./scripts/devserver.sh

.PHONY: webui
webui:
	jurigged server.py

.PHONY: install
install:
	mv scripts/.env.example scripts/.env
	mv subreddits.example.txt subreddits.txt
	mkdir -p logs/
	mkdir -p assets/
	mkdir -p categories/
	echo "" > categories/example.txt

	echo "You can now change your credentials in devserver.sh and subreddits in config"