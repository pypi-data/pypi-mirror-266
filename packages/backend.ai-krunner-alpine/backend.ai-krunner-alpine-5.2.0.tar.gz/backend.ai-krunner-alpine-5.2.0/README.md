# backend.ai-krunner-alpine
Backend.AI Kernel Runner Package for Alpine-based Kernels

## Development & Updating

Please refer [the README of krunner-static-gnu package](https://github.com/lablup/backend.ai-krunner-static-gnu/blob/master/README.md).

## Making a minimal Alpine-based image compatibile with this krunner package

[Use Alpine 3.17 or later and install this list of packages.](https://github.com/lablup/backend.ai-krunner-alpine/blob/master/compat-test.Dockerfile)

## Notes

musl *DOES NOT* support dynamic loading of 3rd-party libraries (i.e., Python binary modules) when the CPython interpreter is built statically.

So we keep the CPython interpreter as dynamic, using the standard build procedure taken from [the Docker Hub's Python library](https://github.com/docker-library/python/blob/a1af335ee34324b2f40d7e90345f9468328f6a00/3.11/alpine3.17/Dockerfile).

As Alpine Linux is the only well-known musl-based Linux distribution, we keep our version compatibility of this package based on the musl's ABI compatibility, which is currently 1.2 in Alpine 3.17.
