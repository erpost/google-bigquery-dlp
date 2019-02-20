from google.cloud import bigquery


def get_tables(project_id, dataset):
    """gets a list of BigQuery Tables for a given Project/Dataset"""
    tables = []
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset)
    dataset_tables = list(client.list_tables(dataset_ref))

    for dataset_table in dataset_tables:
        tables.append(dataset_table.table_id)

    return tables


def get_columns(project_id, dataset, table):
    """gets a list of all Columns for a particular BigQuery Table"""
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset, project_id)
    table_ref = dataset_ref.table(table)
    table = client.get_table(table_ref)
    rows = client.list_rows(table)
    field_names = [field.name for field in rows.schema]

    return field_names


def get_distinct_values(project_id, dataset, table, column):
    client = bigquery.Client(project=project_id)
    query_job = client.query("""SELECT DISTINCT {} FROM `{}.{}.{}`""".format(column, project_id, dataset, table))
    results = query_job.result()

    return results


if __name__ == '__main__':
    project_id = input('Project ID: ')
    dataset = input('Data set: ')

    for table in get_tables(project_id, dataset):
        print('### Table: {} ###'.format(table))
        for column in get_columns(project_id, dataset, table):
            for distinct_value in get_distinct_values(project_id, dataset, table, column):
                print(distinct_value.values()[0])
                print(type(distinct_value.values()[0]))
