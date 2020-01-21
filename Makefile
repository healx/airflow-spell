all:
	bash integration-test/create_env.sh

clean:
	git clean -fX integration-test
