#!python3
import os
import re
import csv
import json
import logging
import time
import requests
import click
import pytoml as toml
import pandas as pd

log = logging.getLogger('telnyx')


def read_input(fn):
    # type: (str) -> pd.DataFrame
    _, ext = os.path.splitext(fn)
    if ext.lower().startswith('.xls'):
        log.info('Opening Excel file [{}]'.format(fn))
        df = pd.read_excel(fn)
    elif ext.lower() == '.csv':
        log.info('Opening CSV file [{}]'.format(fn))
        df = pd.read_csv(fn)
    else:
        raise RuntimeError('This only supports reading Excel or CSV files')
    return df

URL = 'https://lrnlookup.telnyx.com/v1/LRNLookup/'
RE_NOT_DIGITS = re.compile('[^0-9]')


def normalize(phone_number):
    log.debug('normalize got phone number: {}'.format(phone_number))
    phone_number = str(phone_number)
    val = RE_NOT_DIGITS.sub('', phone_number)
    return val


def telnyx_lookup(phone_number, token):
    headers = {'Authorization': 'Token {}'.format(token)}
    phone_number = normalize(phone_number)
    url = URL + phone_number
    log.debug('phone_number: {}'.format(phone_number))
    log.debug('url: {}'.format(url))
    resp = requests.get(url, headers=headers)
    log.debug('resp: {}'.format(resp))
    d = json.loads(resp.text)
    return d


def write_response(response, dst_dir):
    dst_dir = os.path.abspath(os.path.expanduser(dst_dir))
    os.makedirs(dst_dir, exist_ok=True)
    fn = response.get('tn')
    file_path = os.path.join(dst_dir, fn)
    file_path = file_path + '.json'
    with open(file_path, 'w') as f:
        json.dump(response, f, indent=4)
    return


def remove_existing(numbers, dst_dir):
    # type: (list, str) -> list
    if not os.path.exists(dst_dir):
        return numbers
    existing = [fn for fn in os.listdir(dst_dir)]
    existing = [fn.split('.')[0] for fn in existing]
    existing = [normalize(n) for n in existing]
    remaining = [n for n in numbers if normalize(n) not in existing]
    return remaining


@click.command()
@click.option('--config-file', '-c', type=click.Path(exists=True), default='./config.toml', required=True, help='The configuration TOML with API key')
@click.option('--input-file', '-i', type=click.Path(exists=True), default='./input.xlsx', required=True)
@click.option('--field-name', '-n', required=True, help='The column name containing the phone numbers')
@click.option('--output-dir', '-o', type=click.Path(exists=False), default='./telnyx_output', help='The file to output phone number lookup results')
def cli(config_file, input_file, field_name, output_dir):
    with open(config_file) as f:
        config = toml.load(f)
    token = config.get('token')
    if token is None:
        raise RuntimeError('The token is not specified in {}'.format(config_file))
    df = read_input(input_file)
    phone_numbers = list(df[field_name])
    phone_numbers = remove_existing(phone_numbers, output_dir)
    log.info('Received {} phone numbers'.format(len(phone_numbers)))
    lookup_values = []
    log.debug('token: {}'.format(token))
    for phone_number in phone_numbers:
        d_response = telnyx_lookup(phone_number, token)
        write_response(d_response, output_dir)
        time.sleep(.025)  # do 40 requests per second
    


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cli()
