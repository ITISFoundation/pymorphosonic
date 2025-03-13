FROM python:3.9.10 as base
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

ENV INPUT_FOLDER="/input" \
    OUTPUT_FOLDER="/output"

WORKDIR /home/${SC_USER_NAME}

RUN pip install -e git+https://github.com/tjjlemaire/PySONIC.git@6ee5e571edba358dbfa8436c066846fc5d787632#egg=PySONIC
RUN pip install -e git+https://github.com/tjjlemaire/MorphoSONIC.git@19c86216da7939065bc6e719c03d41024a21c3ca#egg=MorphoSONIC

RUN cd /home/scu/src/morphosonic/MorphoSONIC/nmodl && \
    nrnivmodl

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