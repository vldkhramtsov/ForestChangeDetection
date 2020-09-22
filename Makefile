
build:
	docker build -t planet_image .

launch:
	docker run --shm-size 8G -v ${PWD}/:/planet -ti planet_image /bin/bash
	# docker run --runtime nvidia --shm-size 8G -v ${PWD}/:/planet -ti planet_image /bin/bash

# shared memmory issue for PyTorch: https://github.com/pytorch/pytorch/issues/2244
