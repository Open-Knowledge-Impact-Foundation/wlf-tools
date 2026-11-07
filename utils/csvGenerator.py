import csv, json
import os, pprint
SOURCE_DIR = 'frontend/public/locales/'
TARGET_DIR = 'frontend/public/locales/_/csv/'
SOURCE_LANG = 'en'
SOURCE_PATH = os.path.join(SOURCE_DIR, SOURCE_LANG, 'translation.json')
with open(SOURCE_PATH, 'r') as f:
    source_json = json.load(f)

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

def generate_csv(source_json, target_dir):
    source_json = flatten_json(source_json)
    phrases = {}
    languages = os.listdir(SOURCE_DIR)
    for lang in languages:
        if os.path.isdir(os.path.join(SOURCE_DIR, lang)) and lang[0] not in ['.', '_']:
            print("Generating " + lang + " ...")
            target_path = os.path.join(target_dir, lang + '.csv')
            with open(os.path.join(SOURCE_DIR, lang, 'translation.json'), 'r') as f:
                target_json = json.load(f)
            target_json = flatten_json(target_json)
            for key in source_json:
                if key not in target_json:
                    target_json[key] = source_json[key]
            for key in target_json:
                if key  not in phrases:
                    phrases[key] = {
                        'code' : key,
                    }
                phrases[key][lang] = target_json[key]
        entries = list(sorted(phrases.values(), key=lambda x: x['code']))
        languages = [i for i in os.listdir(SOURCE_DIR) if i not in ['_'] and os.path.isdir(os.path.join(SOURCE_DIR, i)) and i[0] != '.']
        target_path = os.path.join(target_dir, 'phrases.csv')




        with open(target_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames = ['code'] + languages, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            writer.writerows(entries)
        cnt = '{| class="wikitable"\n|-\n! Code !! ' + ' !! '.join(languages) + '\n'
        for entry in entries:
            cnt += '|-\n| ' + entry['code'] + ' || ' + ' || '.join([f"<nowiki>{entry.get(i, '')}</nowiki>" for i in languages]) + '\n'
        cnt += '|}'
        with open(os.path.join(target_dir, 'phrases.wiki'), 'w') as f:
            f.write(cnt)
        


def place_nested(d, key, value):
    
    keys = key.split('.')
    for i in keys[:-1]:
        if i not in d:
            d[i] = {}
        d = d[i]
    d[keys[-1]] = value
def update_keys(original, translated):
    for key, value in translated.items():
        if isinstance(value, dict):
            if key in original:
                update_keys(original[key], value)
        else:
            if key in original:
                original[key] = value

def load_from_csv(path, lang):
    phrases = {}
    locale_path = os.path.join(SOURCE_DIR, lang)
    original = {}
    with open(path, 'r', errors='ignore') as f:
            reader = json.load(f)
            try:
                with open(os.path.join(locale_path, "translation.json"), 'r') as f2:
                    original = json.load(f2)
            except FileNotFoundError:
                original = {}
            for code in reader:
                place_nested(phrases, code, reader[code])
            # pprint.pprint(phrases)
            update_keys(original, phrases)
    pprint.pprint(original)

        
    if not os.path.exists(locale_path):
        os.makedirs(locale_path)
    with open(os.path.join(locale_path, 'translation.json'), 'w') as f:
        json.dump(original, f, indent=4, ensure_ascii=False)

load_from_csv("57122723.json", "fr")
# generate_csv(source_json, TARGET_DIR)