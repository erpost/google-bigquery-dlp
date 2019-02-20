import google.cloud.dlp


def detect(project_id, content):
    dlp_client = google.cloud.dlp.DlpServiceClient()

    # Construct the item to inspect.
    item = {'value': content}

    # The info types to search for in the content. Required.
    # info_types = [{'name': 'FIRST_NAME'}, {'name': 'LAST_NAME'}]
    info_types = [{'name': 'ALL_BASIC'}]

    # The minimum likelihood to constitute a match. Optional.
    min_likelihood = 'LIKELIHOOD_UNSPECIFIED'

    # The maximum number of findings to report (0 = server maximum). Optional.
    max_findings = 0

    # Whether to include the matching string in the results. Optional.
    include_quote = True

    # Construct the configuration dictionary. Keys which are None may
    # optionally be omitted entirely.
    inspect_config = {
        'info_types': info_types,
        'min_likelihood': min_likelihood,
        'include_quote': include_quote,
        'limits': {'max_findings_per_request': max_findings},
    }

    # Convert the project id into a full resource id.
    parent = dlp_client.project_path(project_id)

    # Call the API.
    response = dlp_client.inspect_content(parent, inspect_config, item)

    # Print out the results.
    if response.result.findings:
        for finding in response.result.findings:
            try:
                # print('Quote: {}'.format(finding.quote))
                value = finding.quote
            except AttributeError:
                pass
            # print('Info type: {}'.format(finding.info_type.name))
            info_type = finding.info_type.name
            # Convert likelihood value to string respresentation.
            likelihood = (google.cloud.dlp.types.Finding.DESCRIPTOR.fields_by_name['likelihood']
                          .enum_type.values_by_number[finding.likelihood].name)
            # print('Likelihood: {}'.format(likelihood))

    else:
        info_type = 'N/A'
        likelihood = 'N/A'
        try:
            value = content
        except Exception:
            value = '<empty>'
        # print('No findings.')

    return [value, info_type, likelihood]


if __name__ == '__main__':
    project_id = input('Project ID: ')
    answer = detect(project_id, None)
    print('Value: {}'. format(answer[0]))
    print('Info Type: {}'.format(answer[1]))
    print(('Likelihood: {}'.format(answer[2])))
