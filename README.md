# DynDNS
DynDNS (dynamic DNS) can be used to update the DNS A records for one or more 
subdomains by using the TransIP API. It will update the A records with the
ip address of the connection which is used.

> The A records must be created already and have an expiration of 1 day.

# Usage
Before you can use the script you must create an API key and activate the API with
your TransIP account. The API key must be saved in a file with the name `key`.

The script can be run with python with some extra packages installed or run in a
docker container. The script requires a couple of commandline arguments.

This example will use:
- a file named `key` in the current working directory to authorize at the TransIP API
- the domain `example.com`
- the sub domains `subdomain1` and `subdomain2`
- the loginname `test_user` which is the TransIP account
```
./dyndns.py -d example.com -s subdomain1 subdomain2 -l test_user
```

## Run with python
Setup a virtual env with all required packages:
```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Now you can run the script. Example:
```
./dyndns.py -d example.com -s subdomain1 subdomain2 -l test_user
```

## Run with Docker
The dyndns.py script can be run in a docker container.

First build the docker image:
```
docker build -t dyndns:latest <directory_with_dyndns_source>
```

Run DynDNS in a Docker container. This example will use:
- a file named `api_key` in the current working directory to authorize at the TransIP API
- the domain `example.com`
- the sub domains `subdomain1` and `subdomain2`
- the loginname `test_user` which is the TransIP account
```
docker run --rm -it -v `pwd`/<file_with_key>:/app/key:ro dyndns:latest -d example.com -s subdomain1 subdomain2 -l test_user
```

The --it argument is only needed when you want to test the script. It will keep stdin
open and allocate a tty. This way you can see all output of the script.