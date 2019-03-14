from fsplit.filesplit import FileSplit
from google.cloud import dlp_v2
import bq
import csv
import os

dump_file = 'bq_dump.csv'
distinct_file = 'bq_distinct.txt'
distinct_set = set()
dlp_findings_list = []
dlp_findings = 'dlp_findings.csv'
split_dir = './splits/'


def get_key():
    storage_key = os.path.expanduser('~/.gcp/dlp-dev.json')
    return storage_key


if os.path.isfile(get_key()):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_key()

project_id = input('Project ID: ')

dataset = input('Data set: ')

# write full dump file to CSV
with open(dump_file, 'w', newline='') as dump_file:
    out_file = csv.writer(dump_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    out_file.writerow(['Table'] + ['Column'] + ['Value'])

    for table in bq.get_tables(project_id, dataset):
        print('Reading Table: {}'.format(table))
        for column in bq.get_columns(project_id, dataset, table):
            for value in bq.get_distinct_values(project_id, dataset, table, column):
                str_value = str(value.values()[0])
                if len(str_value) < 1:
                    str_value = '<empty>'
                out_file.writerow([table] + [column] + [str_value])
                if type(value.values()[0]) == str:
                    distinct_set.add(value.values()[0])

# write distinct lines to text file
with open(distinct_file, 'w') as distinct_file:
    for item in distinct_set:
        distinct_file.write('{}\n'.format(item))

# split distinct file into multiple files for DLP
fs = FileSplit(file='bq_distinct.txt', splitsize=524288, output_dir='splits')
fs.split()

# instantiate DLP client
dlp_client = dlp_v2.DlpServiceClient()

info_types = [{'name': 'LAST_NAME'},
              {'name': 'US_SOCIAL_SECURITY_NUMBER'},
              {'name': 'US_HEALTHCARE_NPI'}]

# info_types = [{'name': 'ALL_BASIC'}]


inspect_config = {
    'info_types': info_types,
    'min_likelihood': None,
    'include_quote': True,
    'limits': {'max_findings_per_request': None},
}

# open and write header to DLP CSV file
with open(dlp_findings, 'w', newline='') as findings:
    out_file = csv.writer(findings, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    out_file.writerow(['Value'] + ['InfoType'] + ['Likelihood'])

    # iterate over split files
    for split_file in os.listdir(split_dir):
        split_path = split_dir + split_file
        if os.stat(split_path).st_size == 0:
            pass
        with open(split_path, mode='rb') as f:
            item = {'byte_item': {'type': 5, 'data': f.read()}}

        parent = dlp_client.project_path(project_id)
        response = dlp_client.inspect_content(parent, inspect_config, item)

        if response.result.findings:
            for finding in response.result.findings:
                try:
                    value = finding.quote
                    info_type = finding.info_type.name
                    likelihood = (dlp_v2.types.Finding.DESCRIPTOR.fields_by_name['likelihood']
                                  .enum_type.values_by_number[finding.likelihood].name)
                    if value in dlp_findings_list:
                        pass
                    else:
                        print('Value: {} | Info type: {} | Likelihood: {}'
                              .format(value, info_type, likelihood))

                        out_file.writerow([value] + [info_type] + [likelihood])
                        dlp_findings_list.append(value)
                except AttributeError as err:
                    print(err)
        else:
            print('No findings')
            pass
