ARG ARCH=x86_64
FROM --platform=linux/${ARCH} lablup/backendai-krunner-wheels:musllinux_1_2 AS wheels

ARG ARCH
FROM --platform=linux/${ARCH} lablup/backendai-krunner-python:musllinux_1_2

ARG PREFIX=/opt/backend.ai
ARG ARCH

# for installing source-distributed Python packages, we need build-base.
# (we cannot just run manylinux-only wheels in Alpine due to musl-libc)
RUN apk add --no-cache build-base linux-headers
RUN ${PREFIX}/bin/pip install --no-cache-dir -U pip setuptools

COPY --from=wheels /root/wheels/* /root/wheels/
COPY requirements.txt /root/
RUN ${PREFIX}/bin/pip install --no-cache-dir -f /root/wheels -r /root/requirements.txt && \
    ${PREFIX}/bin/pip list

# Create directories to be used for additional bind-mounts by the agent
RUN PYVER_MM="$(echo $PYTHON_VERSION | cut -d. -f1).$(echo $PYTHON_VERSION | cut -d. -f2)" && \
    mkdir -p ${PREFIX}/lib/python${PYVER_MM}/site-packages/ai/backend/kernel && \
    mkdir -p ${PREFIX}/lib/python${PYVER_MM}/site-packages/ai/backend/helpers
RUN if test ! -f "${PREFIX}/bin/python" -a ! -h "${PREFIX}/bin/python" ; then \
      ln -s "${PREFIX}/bin/python3" "${PREFIX}/bin/python"; \
    fi

COPY ttyd_linux.${ARCH}.bin ${PREFIX}/bin/ttyd
COPY licenses/* ${PREFIX}/licenses/wheels
RUN chmod +x ${PREFIX}/bin/ttyd

# Build the image archive
RUN cd ${PREFIX}; \
    tar cf /root/image.tar ./*

LABEL ai.backend.krunner.version=10
CMD ["${PREFIX}/bin/python"]

# vim: ft=dockerfile
