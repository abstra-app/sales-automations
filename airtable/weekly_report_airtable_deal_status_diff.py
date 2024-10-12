from abstra.common import get_persistent_dir
import datetime, json, os


persistent_dir = get_persistent_dir()
save_path = persistent_dir / f'weekly-diff'
base_load_path = persistent_dir / 'deals-status-everyday'
load_paths = []
status_over_week = []


# paths of last 2 files
for i in range(2):
    day = datetime.datetime.now() - datetime.timedelta(days=i*7)
    load_paths.append(base_load_path / f'deals-status-{day.strftime("%Y-%m-%d")}.json')
    print(load_paths[i])


# load data if respective file exists
for path in load_paths:
    if path.exists():
        with open(path, 'r') as f:
            status_over_week.append(json.load(f))


# create a dict for each day comparitng the status of the deals, save to json files
for i in range(1, len(status_over_week)):
    diff = {}

    diff['from'] = status_over_week[i]['date']
    diff['to'] = status_over_week[i-1]['date']
    diff['new_deals'] = {}
    diff['unchanged_deals'] = {}
    
    for id in status_over_week[i-1].keys():
        if id == 'date':
            continue

        if id not in status_over_week[i].keys():
            key = 'new_deals'
        elif status_over_week[i][id] == status_over_week[i-1][id]:
            key = 'unchanged_deals'
        else:
            key = f"{status_over_week[i][id]['status']} -> {status_over_week[i-1][id]['status']}"

        if key not in diff.keys():
            diff[key] = {}
            
        diff[key][id] = status_over_week[i-1][id]['name']

    
    # save json file
    try:
        with open(save_path / f"{diff['to']}.json", 'w') as f:
            json.dump(diff, f, indent=4)
    except FileNotFoundError:
        os.makedirs(save_path)
        with open(save_path / f"{diff['to']}.json", 'w') as f:
            json.dump(diff, f, indent=4)
            
