clear-migrations:
	rm -rf migrations

init: clear-migrations
	python -m staze init

migrate:
	python -m staze migrate

upgrade:
	python -m staze upgrade

test: init migrate upgrade
	python -m staze test

dev: init migrate upgrade
	python -m staze dev -x create_all add_user

prod: init migrate upgrade
	python -m staze prod -x create_all add_user
