requirements:
	poetry export -f requirements.txt --without-hashes --dev > requirements.txt

server:
	uvicorn core.main:app --reload

package_install:
	npm ci

fetch:
	python -m core.fetch

scss_watch:
	./node_modules/sass/sass.js --watch static/scss/main.scss static/css/main.css
