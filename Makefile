.PHONY: test api-test web-test smoke lint feed docker-up

api-test:
	cd apps/api && PYTHONPATH=. pytest -q

web-test:
	cd apps/web && npm test && npm run build

lint:
	bash scripts/defensive-lint.sh

smoke:
	cd apps/api && PYTHONPATH=. python ../../scripts/smoke_v1.py

feed:
	python scripts/generate_feed.py

test: lint api-test web-test smoke

docker-up:
	docker compose up --build
