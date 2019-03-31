FROM ubuntu:latest
MAINTAINER Basabjit "basab401@yahoo.co.in"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev supervisor \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
  

# Install dependencies of supervisor
RUN apt-get -y install python-pkg-resources python-meld3
RUN mkdir -p /etc/supervisor \
    && mkdir -p /var/log/supervisor \
    && mkdir -p /var/run  \
    && mkdir /sudo_access_app
COPY ["./supervisord/supervisord.conf", "/etc/supervisor/"]
COPY ["./supervisord/sudo_access_service.conf", "/etc/supervisor/conf.d/"]
RUN apt-get -y purge   \
    exim4              \
    exim4-base         \
    exim4-config       \
    exim4-daemon-light

WORKDIR /sudo_access_app
COPY ./sudo_access ./sudo_access
COPY ./setup.py .
COPY ./requirements.txt .
COPY ./bin ./bin

# Install the package
RUN pip3 install -r requirements.txt \
    && python3 setup.py install --use_supervisor 1
    # To install wheel instead of egg
    # python3 setup.py sdist bdist_wheel \
    # && pip3 install dist/sudo_access-1.0.1-py3-none-any.whl

RUN apt-get clean -y; apt-get autoclean -y; apt-get autoremove -y

ENTRYPOINT ["/usr/bin/supervisord"]
