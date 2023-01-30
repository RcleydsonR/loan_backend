up:
	docker-compose up

down:
	docker-compose down

migrate:
	docker exec -it loan_management_backend python manage.py migrate

migrations:
	docker exec -it loan_management_backend python manage.py makemigrations

bash:
	docker-compose exec loan_management bash

test:
ifeq ($(TEST),)
	docker-compose run --rm --entrypoint "pytest $(FILE) -s --disable-warnings" loan_management
else
	docker-compose run --rm --entrypoint "pytest $(FILE) -s --disable-warnings -k $(TEST)" loan_management
endif