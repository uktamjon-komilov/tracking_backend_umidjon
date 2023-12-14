run:
	docker compose -f docker-compose.yml up --build

exec:
	docker compose -f docker-compose.yml exec web sh