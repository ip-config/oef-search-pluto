# OEF Search Pluto

## Setup an OEF Search Pluto node

#### Using `oef-search-pluto-image` docker image

- Required: git, docker, python3

- Initial setup:

First we need to define `git pullall` method which will pull our submodules recursively:
```bash
git config --global alias.pullall '!f(){ git pull \"$@\" && git submodule sync --recursive && git submodule update --init --recursive; }; f'
```

- Build and run:

```bash
git clone git@github.com:uvue-git/oef-search-pluto.git && cd oef-search-pluto && git pullall
git checkout master
python3 docker-images/demo_network.py --num_nodes 2 --link 0:1 --http_port_map 0:7500 --log_dir `pwd`/docker-images/logs/ -b --run_director
```

- Run without rebuilding:

```bash
python3 docker-images/demo_network.py --num_nodes 2 --link 0:1 --http_port_map 0:7500 --log_dir `pwd`/docker-images/logs/ --run_director
```
