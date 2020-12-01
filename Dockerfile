FROM ubuntu:20.04

# Change working directory
RUN mkdir src
WORKDIR "/src"
COPY . .

# # Update packages and install dependency packages for services
RUN apt-get update && apt-get upgrade -y && apt-get autoremove -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install software-properties-common -y
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:deadsnakes/ppa

# PYTHON and PIP
RUN apt-get install python3.8
RUN apt-get install -y build-essential python3-pip python3-dev git -y
RUN pip3 -q install pip --upgrade

# MORFEUSZ
RUN apt-key adv --fetch-keys http://download.sgjp.pl/apt/sgjp.gpg.key \
    && apt-add-repository http://download.sgjp.pl/apt/ubuntu \
    && apt-get install -y morfeusz2 \
    && apt-get update \
    && apt-get clean

RUN pip3 install http://download.sgjp.pl/morfeusz/20201129/Linux/20.04/64/morfeusz2-1.9.16-cp38-cp38-linux_x86_64.whl

# SPACY and pl_spacy_model_morfeusz
RUN pip3 install -U spacy==2.2
RUN pip3 install "http://zil.ipipan.waw.pl/SpacyPL?action=AttachFile&do=get&target=pl_spacy_model_morfeusz-0.1.3.tar.gz"
RUN pip3 install 'h5py<3.0.0'

# SCRAPY
RUN pip3 install scrapy

# GENSIM
RUN pip3 install gensim

# JUPYTER NOTEBOOK
RUN pip3 install jupyter

# PANDAS
RUN pip3 install pandas

# RUN ENTRYPOINT
CMD ["./scripts/entrypoint.sh"]