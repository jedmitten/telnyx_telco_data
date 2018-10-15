import os
import csv
import json
import logging
from collections import OrderedDict, namedtuple
import click

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('convert_telnyx')


def read_json_from_dir(dirname):
    rows = []
    for root, _, fns in os.walk(dirname):
        count = len(fns)
        file_no = 1.0
        for fn in [f for f in fns if f.endswith('.json')]:
            fp = os.path.expanduser(os.path.abspath(os.path.join(root, fn)))
            with open(fp) as f:
                d = json.load(f)
            rows.append(d)
            if file_no % 1000 == 0:
                log.info('Reading... {:.03%} ({} of {})'.format(file_no / count, int(file_no), count))
            file_no += 1
    return rows

LINE_TYPES = {
    '0': 'Wired',
    '1': 'Wireless',
    '2': 'VOIP', 
    '': 'Unknown'
}

TN = 'tn'
LRN = 'lrn'
PORTED_STATUS = 'ported_status'
PORTED_DATE = 'ported_date'
OCN = 'ocn'
LINE_TYPE = 'line_type'
SPID = 'spid'
SPID_CN = 'spid_carrier_name'
SPID_CT = 'spid_carrier_type'
ASPID = 'altspid'
ASPID_CN = 'altspid_carrier_name'
ASPID_CT = 'altspid_carrier_type'
HEADERS = OrderedDict([(TN, None), 
                           (LRN, None),
                           (PORTED_STATUS, None),
                           (PORTED_DATE, None),
                           (OCN, None),
                           (LINE_TYPE, None), 
                           (SPID, None), 
                           (SPID_CN, None),
                           (SPID_CT, None),
                           (ASPID, None),
                           (ASPID_CN, None),
                           (ASPID_CT, None),
                           ])


def write_rows_to_csv(rows, filename):
    no = 1
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for row in rows:
            d = {
                TN: row.get(TN),
                LRN: row.get(LRN),
                PORTED_STATUS: row.get(PORTED_STATUS),
                PORTED_DATE: row.get(PORTED_DATE),
                OCN: row.get(OCN),
                LINE_TYPE: LINE_TYPES.get(row.get(LINE_TYPE)),
                SPID: row.get(SPID),
                SPID_CN: row.get(SPID_CN),
                SPID_CT: row.get(SPID_CT),
                ASPID: row.get(ASPID),
                ASPID_CN: row.get(ASPID_CN),
                ASPID_CT: row.get(ASPID_CT),
            }
            writer.writerow(d)
            log.debug('Wrote line {} of {}'.format(no, len(rows)))
            no += 1
    return True


@click.command()
@click.option('-i', '--input-dir', help='The folder where telnyx output JSON is found', type=click.Path(exists=True))
@click.option('-o', '--output-file', help='The CSV file to write to', type=click.Path(exists=False))
def cli(input_dir, output_file):
    log.info('Starting {}'.format(__file__))
    log.info('Read files from [{}]'.format(input_dir))
    rows = read_json_from_dir(input_dir)
    log.info('Read {} files from [{}]'.format(len(rows), input_dir))
    log.info('Writing to [{}]'.format(output_file))
    write_rows_to_csv(rows, output_file)


if __name__ == '__main__':
    cli()
