# Dockerfile describing an environment for CI/CD for Sketchingpy.
# Released under CC-BY-SA

FROM ubuntu:jammy-20230301

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y python-is-python3
RUN apt-get install -y xvfb
RUN apt-get install -y zip
RUN apt-get install -y lftp
RUN apt-get install -y sshpass
RUN apt-get install -y libasound2

# Thanks https://stackoverflow.com/questions/67090130
# CC-BY-SA Matteo Pasini
RUN apt-get install -y wget bzip2 libxtst6 libgtk-3-0 libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev && rm -rf /var/lib/apt/lists/*

RUN mkdir firefox
RUN wget -P /firefox https://ftp.mozilla.org/pub/firefox/releases/110.0.1/linux-x86_64/en-US/firefox-110.0.1.tar.bz2
RUN tar -xf ./firefox/firefox-110.0.1.tar.bz2
ENV PATH firefox:$PATH

RUN pip install Jinja2 matplotlib mypy nose2 numpy Pillow types_Pillow pycodestyle pyflakes pygame-ce pyyaml selenium
