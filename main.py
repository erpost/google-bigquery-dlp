import dlp
import bq
import csv
import os


def get_key():
    storage_key = os.path.expanduser('~/.gcp/dlp-dev.json')
    return storage_key


if os.path.isfile(get_key()):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_key()

project_id = input('Project ID: ')
if len(project_id) < 1:
    project_id = 'allofus-development'
dataset = input('Data set: ')
if len(dataset) < 1:
    dataset = 'test'

outfile = 'bq_dlp.csv'

with open(outfile, 'w', newline='') as outfile:
    out_file = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    out_file.writerow(['Table'] + ['Column'] + ['Value'] + ['DLP Value'] + ['DLP Info Type'] + ['Likelihood'])

    for table in bq.get_tables(project_id, dataset):
        print('### Table: {} ###'.format(table))
        for column in bq.get_columns(project_id, dataset, table):
            for distinct_value in bq.get_distinct_values(project_id, dataset, table, column):
                dist_value = str(distinct_value.values()[0])
                if len(dist_value) < 1:
                    dist_value = '<empty>'
                dlp_distinct_value = dlp.detect(project_id, dist_value)
                print('Table: {}'.format(table))
                print('Value: {}'.format(dist_value))
                print('Info Type: {}'.format(dlp_distinct_value[1]))
                print('Likelihood: {}'.format(dlp_distinct_value[2]))
                out_file.writerow([table] + [column] + [dist_value] + [dlp_distinct_value[0]]
                                  + [dlp_distinct_value[1]] + [dlp_distinct_value[2]])
