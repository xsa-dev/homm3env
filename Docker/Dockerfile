# важно оперативка контейнера должно быть минимум 4гб (свап на 4гб не пробовал)

FROM ubuntu:20.04
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# environment
RUN apt update
RUN apt-get install build-essential -y
RUN apt-get install git cmake libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev libsdl2-mixer-dev zlib1g-dev libavformat-dev libswscale-dev libboost-dev libboost-filesystem-dev libboost-system-dev libboost-thread-dev libboost-program-options-dev libboost-locale-dev qtbase5-dev libtbb-dev libluajit-5.1-dev -y
RUN git clone -b develop --depth 1 --recursive https://github.com/vcmi/vcmi.git

# build
RUN mkdir build && cd build
WORKDIR /build
RUN cmake ../vcmi
RUN cmake --build . --

# gamedata ports
RUN export XDG_DATA_DIRS=/root/.local/share
RUN export XDG_CACHE_DIRS=/root/.local/share
RUN export XDG_CONFIG_DIRS=/root/.local/share
RUN export XDG_RUNTIME_DIR=/root/.local/share

# ports
EXPOSE 3030