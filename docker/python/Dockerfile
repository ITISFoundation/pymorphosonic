FROM python:3.11 as base
#
#  USAGE:
#     cd services/pymorphosonic
#     docker build -f Dockerfile -t pymorphosonic:prod --target production ../../
#     docker run pymorphosonic:prod
#

LABEL maintainer=lmoyasans

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu
RUN adduser --uid ${SC_USER_ID} --disabled-password --gecos "" --shell /bin/sh --home /home/${SC_USER_NAME} ${SC_USER_NAME}

RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    jq \
    && rm --recursive --force /var/lib/apt/lists/*

FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production

ENV INPUT_FOLDER="/tmp/input" \
    OUTPUT_FOLDER="/tmp/output"

WORKDIR /home/${SC_USER_NAME}

RUN pip install -e git+https://github.com/tjjlemaire/PySONIC.git@aff881012b83731e7139aa1994f5dff358525700#egg=pysonic
RUN pip install -e git+https://github.com/tjjlemaire/MorphoSONIC.git@64a0a2325ec8a1cfa90ce5595ea93301e4a1ff91#egg=morphosonic

# copy docker bootup scripts
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} docker/python/*.sh docker/
# copy src code
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} src/pymorphosonic src/pymorphosonic
# copy simcore service cli
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} service.cli/ service.cli/
# necessary to be able to call run directly without sh in front
ENV PATH="/home/${SC_USER_NAME}/service.cli:${PATH}"
RUN pip install -r src/pymorphosonic/requirements.txt

ENTRYPOINT [ "/bin/sh", "docker/entrypoint.sh", "/bin/sh", "-c" ]
## only for computational (also the "/bin/sh", "-c" above)
CMD ["run"] 