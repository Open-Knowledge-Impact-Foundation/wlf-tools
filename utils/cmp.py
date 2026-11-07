import json, os, copy
orig = 'en'
new = 'bn'
LOCALE_DIR = 'frontend/public/locales/'
with open('frontend/public/locales/' + orig + '/translation.json', 'r') as f:
    original_data = f.read()


# Load JSON data
original_json : dict[str, str] = json.loads(original_data)
def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            for a in x:
                flatten(a, name)
        else:
            out[name[:-1]] = x
    flatten(y)
    return out
# Function to update keys
def update_keys(original, translated):
    for key, value in translated.items():
        if isinstance(value, dict):
            if key in original:
                update_keys(original[key], value)
        else:
            if key in original:
                original[key] = value


def update_with_new_keys(target):
    merged_results = copy.deepcopy(original_json)
    NEW_PATH = 'frontend/public/locales/' + target + '/translation.json'
    try:
        with open(NEW_PATH, 'r') as f:
            current_translation = json.load(f)
    except :
        current_translation = {}
    update_keys(merged_results, current_translation)
    # Convert updated dictionary back to JSON
    updated_json = json.dumps(merged_results, indent=4, ensure_ascii=False)
    with open(NEW_PATH, 'w') as f:
        f.write(updated_json)
    phrases = flatten_json(merged_results)
    print(phrases.get("campaign.submission.action.see"))
    tr_path = os.path.join("translations", "campwiz", target, "root.json")
    if not os.path.exists(os.path.dirname(tr_path)):
        os.makedirs(os.path.dirname(tr_path))
    with open(tr_path, 'w') as f:
        json.dump(phrases, f, indent=4, ensure_ascii=False)
    
for i in os.listdir(LOCALE_DIR):
    if i not in [orig, '_']:
        print("Updating " + i + " ...")
        update_with_new_keys(i)