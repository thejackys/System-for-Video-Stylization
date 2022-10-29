FROM nvidia/cuda:11.0.3-base-ubuntu20.04
WORKDIR "/root"
# RUN apt-get update && apt-get install -y curl
# RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
# RUN apt-get update && apt-get install -y nodejs python3 python3-pip
RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Asia/Taipei apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    libopencv-core4.2 \
    libopencv-contrib4.2 \
    qt5-default \
    libfftw3-bin \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install torch==1.11.0+cpu torchvision==0.12.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install tensorflow-cpu flask flask_cors opencv-python-headless tqdm shutils