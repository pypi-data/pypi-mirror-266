FROM python:latest

ARG KRONOS_SRC=/kronos_src
ARG KRONOS_FROM_PIP=yes

RUN useradd -u 9999 cthulhu && mkdir /home/cthulhu && chown cthulhu /home/cthulhu

RUN if [ -d "$KRONOS_SRC" ]; then \
        echo "Installing from local directory: $KRONOS_SRC" ;\
        pip install "$KRONOS_SRC"[test] ;\
    elif [ "$KRONOS_FROM_PIP" = "yes" ]; then \
        echo "Installing from pip" ;\
        pip install dg645-ioc ;\
    else \
        echo "\n  ***\n  *** Source not found at \$KRONOS_SRC ($KRONOS_SRC) -- failing build now. \n  ***\n" ;\
        /bin/false ;\
    fi

USER cthulhu

ENTRYPOINT dg645-ioc
