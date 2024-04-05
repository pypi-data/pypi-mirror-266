FROM python:3.12.2-alpine
ARG PREFIX=/opt/backend.ai

ENV PATH=${PREFIX}/bin:$PATH
ENV LANG=C.UTF-8
ENV PYTHON_VERSION 3.12.2

RUN mkdir -p ${PREFIX}; \
    mv /usr/local/* ${PREFIX}; \
    sed -i "s@/usr/local@${PREFIX}@g" ${PREFIX}/bin/pip*; \
    sed -i "s@/usr/local@${PREFIX}@g" ${PREFIX}/bin/idle3.11; \
    sed -i "s@/usr/local@${PREFIX}@g" ${PREFIX}/bin/2to3-3.11; \
    sed -i "s@/usr/local@${PREFIX}@g" ${PREFIX}/bin/pydoc3.11; \
    sed -i "s@/usr/local@${PREFIX}@g" ${PREFIX}/bin/python3.11-config; \
    sed -i "s@/usr/local@${PREFIX}@g" ${PREFIX}/bin/wheel; \
    :

CMD ["python3"]

# vim: ft=dockerfile
