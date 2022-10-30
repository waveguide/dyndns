#!/usr/bin/env python3
import json
import uuid
import signal
import time
import sys
import argparse
from base64 import b64encode
from ipaddress import IPv4Address

from loguru import logger
import requests
from requests.exceptions import HTTPError, Timeout
from OpenSSL import crypto

API_URI = "https://api.transip.nl/v6"
MYIP_URI = "https://ipinfo.io/ip"
TIMEOUT = 10  # Timeout for http requests


def get_my_ip() -> IPv4Address:
    """Return the public ip address of the current connection"""
    resp = requests.get(MYIP_URI, timeout=TIMEOUT)
    resp.raise_for_status()

    return IPv4Address(resp.text)


def sign(msg: str) -> str:
    """Sign message and return signature as base64 string"""
    with open("key", "rb") as fp:
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, fp.read())
    signature = crypto.sign(pkey, msg.encode(), "sha512")

    return b64encode(signature).decode()


def get_token(login: str, expiration_secs: int) -> str:
    """Get authorization token"""
    payload = json.dumps(
        {
            "login": login,
            "nonce": uuid.uuid4().hex,
            "read_only": False,
            "expiration_time": f"{expiration_secs} seconds",
            "label": "DynDNS",
            "global_key": True,
        }
    )

    uri = f"{API_URI}/auth"
    headers = {
        "Content-Type": "application/json",
        "Signature": sign(payload),
    }
    resp = requests.post(uri, data=payload, headers=headers, timeout=TIMEOUT)
    if resp.status_code != 201:
        logger.error(f"get token failed: {resp.status_code}/{resp.text}")
    resp.raise_for_status()

    return resp.json()["token"]


def update_dns(name: str, domain: str, ip: IPv4Address, token: str):
    """Update a single DNS entry"""
    uri = f"{API_URI}/domains/{domain}/dns"
    payload = {
        "dnsEntry": {
            "name": name,
            "expire": 86400,
            "type": "A",
            "content": str(ip),
        }
    }
    resp = requests.patch(
        uri,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=TIMEOUT,
    )
    if resp.status_code != 204:
        logger.error(
            f"Update DNS for {name}.{domain} failed: {resp.status_code}/{resp.text}"
        )
    resp.raise_for_status()


def sig_handler(signum, frame):
    """Handle signal"""
    logger.info(f"Stopping after handling signal: {signal.Signals(signum).name}")
    sys.exit(0)


def start(loginname: str, domain: str, subdomains: list, interval: int):
    """Update DNS periodically"""
    last_known_ip = None

    while True:
        try:
            my_ip = get_my_ip()
            logger.info(f"Current ip is {my_ip}")
            if my_ip == last_known_ip:
                logger.info(f"No Need to update DNS since ip is still {my_ip}")
                time.sleep(interval)
                continue

            token = get_token(loginname, interval - 10)

            for subdomain in subdomains:
                logger.info(f"Set DNS for {subdomain}.{domain} to {my_ip}")
                update_dns(subdomain, domain, my_ip, token)

            last_known_ip = my_ip
            time.sleep(interval)
        except (HTTPError, Timeout) as e:
            logger.error(f"Got exception: {e}")
            time.sleep(args.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update DNS A records for one or more sub domains of a single domain."
    )
    parser.add_argument(
        "-l", "--loginname", required=True, help="Login name used at TransIP"
    )
    parser.add_argument(
        "-d", "--domain", required=True, help="Domain name. E.g. example.com"
    )
    parser.add_argument(
        "-s",
        "--subdomains",
        nargs="+",
        required=True,
        help="Sub domains separated by a space",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=60,
        help="Check every x seconds. Default and minimum value is 60 seconds",
    )
    args = parser.parse_args()
    if args.interval < 60:
        sys.exit("Interval may not be less than 60 seconds")

    logger.info("Start")
    logger.info(f"Interval: {args.interval} seconds")

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    start(args.loginname, args.domain, args.subdomains, args.interval)
