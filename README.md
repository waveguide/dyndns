# DynDNS
DynDNS (dynamic DNS) can be used to update the DNS A records for one or more 
subdomains by using the TransIP API. It will update the A records with the
ip address of the connection which is used.

> The A records must be created already and have an expiration of 1 day.

# Docker
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