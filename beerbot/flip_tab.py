


import json



with open('beertab.json', 'r') as f:
    beertab = json.loads(f.read())


new_beertab = {}


for k, v in beertab.items():
    new_beertab[k] = {
        'name': v.get('name'),
        'balance': -1 * v['balance']
    }



with open('beertab.json', 'w') as f:
    f.write(json.dumps(new_beertab))