test: staze-test blog-test

staze-test:
	pytest -x

blog-init:
	$(MAKE) -C staze/tests/blog	init PYTHONPATH=$(PWD)

blog-migrate:
	$(MAKE) -C staze/tests/blog	migrate PYTHONPATH=$(PWD)

blog-upgrade:
	$(MAKE) -C staze/tests/blog	upgrade PYTHONPATH=$(PWD)

blog-test:
	$(MAKE) -C staze/tests/blog	test PYTHONPATH=$(PWD)

blog-dev:
	$(MAKE) -C staze/tests/blog	dev PYTHONPATH=$(PWD)

blog-prod:
	$(MAKE) -C staze/tests/blog	prod PYTHONPATH=$(PWD)
