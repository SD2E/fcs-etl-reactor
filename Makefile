.PHONY: tests container tests-local tests-reactor tests-deployed
.SILENT: tests container tests-local tests-reactor tests-deployed

# only do this if you're sure it works
all: container deploy after
	true

clean:
	rm -rf .hypothesis .pytest_cache __pycache__ */__pycache__ tmp.*

# there's code in reactor.py that is definitely not Py3 safe yet
# container-py3:
# 	bash tests/run_deploy_with_updates.sh -R -k -F Dockerfile.py3

container:
	bash tests/run_deploy_with_updates.sh -R -k -F Dockerfile

shell:
	bash tests/run_container_tests.sh bash

tests-local: clean
	bash tests/run_container_tests.sh pytest tests -s -vvv ${PYTESTOPTS}

tests-reactor: clean
	bash tests/run_local_message.sh

tests-deployed: clean
	bash tests/run_deployed_message.sh

tests: tests-local tests-reactor
	true

deploy: clean
	bash tests/run_deploy_with_updates.sh

after:
	bash tests/run_after_deploy.sh
