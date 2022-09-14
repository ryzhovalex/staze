test: staze-test blog-test

staze-test:
	pytest -x --ignore=blog

blog-init:
	$(MAKE) PYTHONPATH=$(PWD) -C staze/tests/blog	init

blog-migrate:
	$(MAKE) PYTHONPATH=$(PWD) -C staze/tests/blog	migrate

blog-upgrade:
	$(MAKE) PYTHONPATH=$(PWD) -C staze/tests/blog	upgrade

blog-test:
	$(MAKE) PYTHONPATH=$(PWD) -C staze/tests/blog	test

blog-dev:
	$(MAKE) PYTHONPATH=$(PWD) -C staze/tests/blog	dev

blog-prod:
	$(MAKE) PYTHONPATH=$(PWD) -C staze/tests/blog	prod
