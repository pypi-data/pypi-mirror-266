FROM python:latest


ARG SYNCSTER_SRC=/syncster_src
ARG SYNCSTER_IOC_SRC=/syncster_ioc_src

ARG SYNCSTER_FROM_PIP=yes
ARG SYNCSTER_IOC_FROM_PIP=yes

RUN useradd -u 9999 cthulhu && mkdir /home/cthulhu && chown cthulhu /home/cthulhu

RUN if [ -d "$SYNCSTER_SRC" ]; then \
        echo "Installing from local directory: $SYNCSTER_SRC" ;\
        pip install "$SYNCSTER_SRC"[test] ;\
    elif [ "$SYNCSTER_FROM_PIP" = "yes" ]; then \
        echo "Installing from pip" ;\
        pip install menlo-syncro[test] ;\
    else \
        echo "\n  ***\n  *** Source not found at \$SYNCSTER_SRC ($SYNCSTER_SRC). \n  ***\n" ;\
    fi

RUN if [ -d "$SYNCSTER_IOC_SRC" ]; then \
        echo "Installing from local directory: $SYNCSTER_IOC_SRC" ;\
        pip install "$SYNCSTER_IOC_SRC"[test] ;\
    elif [ "$SYNCSTER_IOC_FROM_PIP" = "yes" ]; then \
        echo "Installing from pip" ;\
        pip install syncster-ioc[test] ;\
    else \
        echo "\n  ***\n  *** Source not found at \$SYNCSTER_IOC_SRC ($SYNCSTER_IOC_SRC) -- failing build now. \n  ***\n" ;\
        /bin/false ;\
    fi

USER cthulhu

ENTRYPOINT syncster-ioc
