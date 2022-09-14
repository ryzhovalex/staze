test: staze-test blog-test

staze-test:
	pytest -x

blog-test:
	$(MAKE) -C staze/tests/blog	test PYTHONPATH=$(PWD)

blog-dev:
	$(MAKE) -C staze/tests/blog	dev PYTHONPATH=$(PWD)

blog-prod:
	$(MAKE) -C staze/tests/blog	prod PYTHONPATH=$(PWD)
