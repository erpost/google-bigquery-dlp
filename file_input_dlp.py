import os
import dlp


project_id = 'allofus-development'


def get_key():
    storage_key = os.path.expanduser('~/.gcp/dlp-dev.json')
    return storage_key


if os.path.isfile(get_key()):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_key()

infile = 'bq_distinct.csv'

with open(infile) as f:
    for line in f:
        print(line)
        # print(dlp.detect(project_id, line))
