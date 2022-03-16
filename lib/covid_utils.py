import json
from datetime import datetime

import requests
from matplotlib import pyplot as plt


def incidence_image(path: str):
    base_url = 'https://api.corona-zahlen.org'
    # total
    germany_incidence = get_from_api(f'{base_url}/germany', ['weekIncidence'])
    germany_last_incidence = get_from_api(f'{base_url}/germany/history/incidence/2', ['data', 0, 'weekIncidence'])

    # bavaria
    bavaria_incidence = get_from_api(f'{base_url}/states', ['data', 'BY', 'weekIncidence'])
    bavaria_last_incidence = get_from_api(f'{base_url}/states/history/incidence/2',
                                          ['data', 'BY', 'history', 0, 'weekIncidence'])

    # districts
    districts = ['09184', '09178', '09162', '09175', '09274', '05112']
    data = json.loads(requests.get(f'{base_url}/districts/').text)
    incidences, names, incidences_before = {}, {}, {}
    for district in districts:
        try:
            district_data = data['data'][district]
            incidences[district] = district_data['weekIncidence']
            names[district] = district_data['county']
        except KeyError:
            districts.remove(district)
            print(f'couldn\'t find district {district} (or JSON malformed)')
    # districts change
    data_before = json.loads(requests.get(f'{base_url}/districts/history/incidence/2').text)
    for district in districts:
        incidences_before[district] = \
            get_from_dict(data_before, ['data', district, 'history', 0, 'weekIncidence'])

    create_incidence_image(bavaria_incidence, bavaria_last_incidence, data, germany_incidence,
                           germany_last_incidence, incidences, incidences_before, names, path)


def get_from_api(url, keys):
    val = json.loads(requests.get(url).text)
    try:
        for key in keys:
            val = val[key]
        return val
    except KeyError:
        return 0


def get_from_dict(data, keys):
    val = data
    try:
        for key in keys:
            val = val[key]
        return val
    except KeyError:
        return None


def create_incidence_image(bavaria_incidence, bavaria_last_incidence, data, germany_incidence,
                           germany_last_incidence, incidences, incidences_before, names, path):
    plt.figure(figsize=(8, 5))
    sorted_incidences = sorted(incidences.items(), key=lambda x: x[1])[::-1]
    container = plt.bar(
        list(names[a] for a, _ in sorted_incidences) + ['Deutschland\n(gesamt)', 'Bayern\n(gesamt)'],
        list(b for _, b in sorted_incidences) + [germany_incidence, bavaria_incidence],
        align='center', width=0.3, color='#8ec07c')
    plt.axhline(y=1000, linewidth=1, color='red')
    plt.bar_label(container=container, labels=list(
        format_incidence_change(v, incidences_before[k]) for k, v in sorted_incidences)
                                              + [format_incidence_change(germany_incidence,
                                                                         germany_last_incidence),
                                                 format_incidence_change(bavaria_incidence,
                                                                         bavaria_last_incidence)])
    plt.title('Wöchentliche Inzidenzen')
    plt.xlabel('Zuletzt aktualisert: ' + datetime.fromisoformat(data['meta']['lastUpdate'][:-1])
               .strftime('%d.%m. %H:%M') + '\n(Veränderungen: täglich)',
               labelpad=15)
    plt.ylabel('')
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, y1, y2 + 110))
    plt.subplots_adjust(bottom=-1)
    plt.tight_layout()
    plt.savefig(path)


def format_incidence_change(incidence, incidence_before):
    if incidence is None or incidence == 0:
        return 'N/A'
    s = '{:.2f}'.format(incidence) + '\n('
    if incidence_before is None or incidence_before == 0:
        return s + 'N/A)'
    ratio = incidence / incidence_before
    if ratio > 1.0:
        s += '+'
    s += '{:.2%}'.format(ratio - 1.0) + ')'
    return s
