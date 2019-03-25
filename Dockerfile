FROM ubuntu:16.04 as build_base

WORKDIR /edx/edxapp

COPY requirements requirements

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
        libxmlsec1-dev \
        libxslt1.1 \
        libxslt1-dev \
        pkg-config \
        python-pip \
        swig \
    && \
    pip install --global-option=build_ext --compile --no-cache-dir numpy==1.6.2 Cython==0.21.2 && \
    pip install --global-option=build_ext --compile --no-cache-dir scipy==0.14.0 && \
    pip install --no-cache-dir -r requirements/edx/pre.txt && \
    pip install --global-option=build_ext --compile --no-cache-dir -r requirements/edx/paver.txt && \
    pip install --no-cache-dir -r requirements/edx/base.txt && \
    pip install --no-cache-dir git+https://github.com/edx/nltk.git@2.0.6#egg=nltk==2.0.6 && \
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


# Build static files for final image
FROM nodejs_base as static_compile

COPY . .
RUN pip install --no-cache-dir -r requirements/edx/local.txt
RUN . .node/bin/activate && \
    paver install_node_prereqs && \
    paver update_assets cms --settings aws && \
    paver update_assets lms --settings aws && \
    echo "Done"



