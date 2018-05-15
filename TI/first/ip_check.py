import ipaddress
import json
import requests
import sys

from iso3166 import countries

API_URL="https://ipinfo.io/{}/geo"

def parse_ip(line):
    try:
        ip = unicode(line.strip())
        return ipaddress.ip_address(ip).exploded
    except:
        return None


def get_ips(inp):
    with open(inp, 'r') as f:
        for line in f:
            ip = parse_ip(line)
            if ip:
                yield ip
            else:
                print >> sys.stderr, 'Line {} does not contein correct ip adress'.format(line)


def get_countries(ips):
    '''bulk requests does not work for this API'''
    for ip in ips:
        res = requests.get(API_URL.format(ip))
        if res.status_code == 200:
            geo = res.json()
            if not geo.get('bogon'):
                try:
                    country = countries.get(geo.get('country'))
                    yield country.alpha3, ip
                except:
                    print >> sys.stderr, 'Could not determine country for ip address {}, API result was {}'.format(ip, geo)
            else:
                print 'ip address {} is a "bogon" address'.format(ip)
                yield 'BOGON', ip


def unique(input_file):
    #count only unique ip addresses
    results = {}
    for c,ip in get_countries(get_ips(input_file)):
        country = results.setdefault(c, set())
        country.add(ip)

    return {k:len(v) for k,v in results.items()}


def non_unique(input_file):
    #count non-unique ip addresses
    results = {}
    for c,ip in get_countries(get_ips(input_file)):
        country = results.get(c,0)
        results[c] = country+1

    return results

