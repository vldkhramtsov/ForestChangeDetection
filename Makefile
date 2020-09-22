
build:
	docker build -t clearcut_image .

launch:
	docker run -v ${PWD}/:/sentinel -ti clearcut_image /bin/bash
