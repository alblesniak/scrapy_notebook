FROM ubuntu:20.04

# Change working directory
RUN mkdir src
WORKDIR "/src"
COPY . .

# # Update packages and install dependency packages for Ubuntu
RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install software-properties-common -y
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y \
    build-essential \
    libssl-dev \
    libpq-dev \
    libcurl4-gnutls-dev \
    libexpat1-dev \
    libxft-dev \
    chrpath \
    libfreetype6 \
    libfreetype6-dev \
    libfontconfig1 \
    libfontconfig1-dev \
    wget \
    curl \
    python3.8 \
    python3-setuptools \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-urllib3 \
    git

# PIP
RUN pip3 -q install pip --upgrade

# MORFEUSZ
RUN apt-key adv --fetch-keys http://download.sgjp.pl/apt/sgjp.gpg.key \
    && apt-add-repository http://download.sgjp.pl/apt/ubuntu \
    && apt-get install -y morfeusz2 \
    && apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install http://download.sgjp.pl/morfeusz/20201129/Linux/20.04/64/morfeusz2-1.9.16-cp38-cp38-linux_x86_64.whl

# SPACY and pl_spacy_model_morfeusz
RUN pip3 install -U spacy==2.2
RUN pip3 install "http://zil.ipipan.waw.pl/SpacyPL?action=AttachFile&do=get&target=pl_spacy_model_morfeusz-0.1.3.tar.gz"
RUN pip3 install 'h5py<3.0.0'

# SCRAPY
RUN pip3 install scrapy
RUN pip3 install scrapy-rotating-proxies

# GENSIM
RUN pip3 install gensim

# JUPYTER NOTEBOOK
RUN pip3 install jupyter

# PANDAS
RUN pip3 install pandas

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
RUN rm -rf /tmp/chromedriver.zip

# set display port to avoid crash
ENV DISPLAY=:99

# SELENIUM
RUN pip3 install selenium

# DATABASES
RUN pip3 install sqlalchemy

# RUN ENTRYPOINT
CMD ["./scripts/entrypoint.sh"]