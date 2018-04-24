.PHONY: tests container tests-local tests-reactor tests-deployed data-representation
.SILENT: tests container tests-local tests-reactor tests-deployed data-representation

data-representation:
	git submodule update --init

clean:
	rm -rf .hypothesis .pytest_cache __pycache__ */__pycache__
	bash tests/remove_images.sh

container-py3: data-representation
	bash tests/run_deploy_with_updates.sh -R -k -F Dockerfile.py3

container: data-representation
	bash tests/run_deploy_with_updates.sh -R -k -F Dockerfile

shell:
	bash tests/run_container_tests.sh bash

tests-local:
	bash tests/run_container_tests.sh pytest tests -s -vvv

tests-reactor:
	bash tests/run_local_message.sh

tests-deployed:
	bash tests/run_deployed_message.sh

tests: tests-local tests-reactor
	true

trial-deploy:
	bash tests/run_deploy_with_updates.sh test

deploy:
	bash tests/run_deploy_with_updates.sh

after:
	bash tests/run_after_deploy.sh
