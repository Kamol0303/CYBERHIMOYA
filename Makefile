.PHONY: test api-test web-test smoke lint feed feed-keys docker-up api-dev extension-validate

api-test:
	cd apps/api && PYTHONPATH=. pytest -q

web-test:
	cd apps/web && npm test && npm run build

lint:
	bash scripts/defensive-lint.sh

extension-validate:
	bash scripts/validate_extension.sh

smoke:
	cd apps/api && PYTHONPATH=. python ../../scripts/smoke_v1.py

feed:
	python scripts/generate_feed.py

feed-keys:
	python scripts/generate_feed_keys.py

api-dev:
	cd apps/api && PYTHONPATH=. uvicorn app.main:app --reload --port 8000

test: lint extension-validate api-test web-test smoke

docker-up:
	docker compose up --build
