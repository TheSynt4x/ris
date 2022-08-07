.PHONY: fmt
fmt:
	black .
	isort .
	autoflake --in-place --remove-all-unused-imports --recursive .

.PHONY: lint
lint:
	black --check .
	isort --check-only .
	flake8 .

.PHONY: devserver
devserver:
	sh ./scripts/devserver.sh

.PHONY: install
install:
	mv scripts/devserver.example.sh scripts/devserver.sh
	mv subreddits.example.txt subreddits.txt
	mkdir -p logs/
	mkdir -p assets/
	mkdir -p categories/
	echo "" > categories/example.txt

	echo "You can now change your credentials in devserver.sh and subreddits in config"