# OEF Search Pluto

## Setup an OEF Search Pluto node

#### Using `oef-search-pluto-image` docker image

- Required: git, docker, python3, gensim, nltk 
    * to install gensim: `pip3 install gensim`
    * to install nltk: `pip3 install nltk`

- Initial setup:

```bash
git clone https://github.com/fetchai/oef-search-pluto && cd oef-search-pluto
git checkout master
git submodule update --init --recursive

```

- Build and run:

```bash
python3 docker-images/demo_network.py --num_nodes 2 --link 0:1 --http_port_map 0:7500 --log_dir `pwd`/docker-images/logs/ -b --run_director
```

- Run without rebuilding:

```bash
python3 docker-images/demo_network.py --num_nodes 2 --link 0:1 --http_port_map 0:7500 --log_dir `pwd`/docker-images/logs/ --run_director
```
