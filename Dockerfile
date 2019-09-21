FROM ubuntu:16.04 as build_base

WORKDIR /edx/app/edxapp/edx-platform

COPY requirements requirements
RUN mkdir -p /edx/app/edxapp/themes
RUN mkdir -p /edx/var/edxapp/static_collector

ENV CFLAGS="-O2 -g0 -Wl,--strip-all"

# Do all the heavy stuff in one layer to cleanup after and reduce overall image size
RUN apt-get update && apt-get install -y \
        build-essential \
        gettext \
        gfortran \
        git \
        graphviz \
        graphviz-dev \
        libffi6 \
        libffi-dev \
        libfreetype6 \
        libfreetype6-dev \
        libgeos-c1v5 \
        libgeos-dev \
        libjpeg8 \
        libjpeg8-dev \
        liblapack3 \
        liblapack-dev \
        libmysqlclient20 \
        libmysqlclient-dev \
        libpng12-0 \
        libpng12-dev \
        libssl1.0.0 \
        libssl-dev \
        libxml2 \
        libxml2-dev \
        libxmlsec1 \
        libxmlsec1-openssl \
        libxmlsec1-dev \
        libxslt1.1 \
        libxslt1-dev \
        pkg-config \
        python-pip \
        swig \
    && \
    pip install --global-option=build_ext --compile --no-cache-dir numpy==1.6.2 && \
    pip install --global-option=build_ext --compile --no-cache-dir scipy==0.14.0 && \
    pip install --global-option=build_ext --compile --no-cache-dir -r requirements/edx/paver.txt && \
    pip install --no-cache-dir -r requirements/edx/base.txt && \
    rm -rf ~/.cache && \
    apt-get purge -y --auto-remove \
        build-essential \
        gfortran \
        graphviz-dev \
        libffi-dev \
        libfreetype6-dev \
        libgeos-dev \
        libjpeg8-dev \
        liblapack-dev \
        libmysqlclient-dev \
        libpng12-dev \
        libssl-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libxslt1-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Prebuild all node dependciesi to store them in layer cache
FROM build_base as nodejs_base

RUN apt-get update && apt-get install -y nodejs npm
COPY package.json package.json
RUN nodeenv --node=6.11.1 --prebuilt --force .node && \
    . .node/bin/activate && \
    npm install


# Copy actual code to image and install dependencies that come along with it
FROM build_base as edxapp

COPY . .
RUN pip install --no-cache-dir -r requirements/edx/local.txt
RUN pip install -e common/lib/xmodule

# Build static files for final image
FROM nodejs_base as static_compile

RUN npm install -g rtlcss
COPY . .
RUN pip install --no-cache-dir -r requirements/edx/local.txt

RUN sed -i 's#\(\W\)_(#\1(#g' /usr/local/lib/python2.7/dist-packages/rest_framework/fields.py
ENV STATIC_COLLECTOR_ROOT=/static_collector \
    STATIC_ROOT_LMS=/static_collector \
    STATIC_ROOT_CMS=/static_collector/studio \
    STATIC_ROOT=/staticfiles \
    NO_PREREQ_INSTALL=True \
    WEBPACK_CONFIG_PATH=webpack.prod.config.js \
    LOCALE_PATHS=/edx/app/edxapp/edx-platform/conf/locale

RUN ./compile.sh

FROM edxapp

COPY --from=static_compile /staticfiles /staticfiles
COPY --from=static_compile /static_collector/webpack-stats.json /staticfiles/webpack-stats.json
COPY --from=static_compile /staticfiles /staticfiles/studio
COPY --from=static_compile /static_collector/webpack-stats.json /staticfiles/studio/webpack-stats.json
