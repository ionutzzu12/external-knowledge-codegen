import json
from components.vocab import Vocab, VocabEntry
from datasets.conala.util import tokenize_intent
import os
print(os.getcwd())


def canonic_fname(name):
    objs = ['list', 'str', 'dict']

    if name in objs: return name

    if name.split('.')[0] in objs:
        new_name = '_'.join(name.split('.')[1:])
    else:
        new_name = name.replace('.', '_')
    return new_name


data = json.load(open('data/train_doc.json'))
sep = '<sep>'
mandatory = '<mandatory>'
optional = '<optional>'

res_funcs = {}

cnt = set()
for e in data:
    if 'functions' in e:
        for f in e['functions']:
            name = f['module'] + '.' + f['name'] if f['module'] not in ['built-in', 'stdtypes'] else f['name']
            key = canonic_fname(name)

            # if name == 'replace':
            #     print('here')
            # TODO tokenize desc
            # encoded_func = name + ' ' + f['return_type']['name'] + ' ' + f['is_method']  # + ' ' + ' '.join(f['description'])
            description = []
            for s in f['description']:
                description += tokenize_intent(s)

            encoded_func = [name, f['return_type']['name'], f['is_method']] + description

            encoded_func2 = encoded_func
            for param in f['parameters']:
                # encoded_func2 += sep + param['name'] + ' ' + param['types'][0]['name'] + ' ' + param['description'] + mandatory
                encoded_func2 += [sep, param['name'], param['types'][0]['name']] + tokenize_intent(param['description']) + [mandatory]
                # encoded_func2 += param['name'] + ' ' + param['types'][0]['name']

            encoded_func3 = encoded_func2
            for param in f['optional_parameters']:
                # encoded_func3 += sep + param['name'] + ' ' + param['types'][0]['name'] + ' ' + param['description'] + optional
                encoded_func3 += [sep, param['name'], param['types'][0]['name']] + tokenize_intent(param['description']) + [mandatory]
                # encoded_func3 += param['name'] + ' ' + param['types'][0]['name']

            value = {'name': name, 'doc': encoded_func3}
            # value = {'name': name, 'doc': encoded_func3}

            if key in res_funcs:
                orig = res_funcs[key]
                if not orig == value:
                    print('ERR', f)
                    print('diff:', '\n\t', orig['doc'], '\n\t', value['doc'])
                    cnt.add(name)
            else:
                res_funcs[key] = value

json.dump(res_funcs, open('data/train_doc_processed.json', 'w'), indent=2)

print('done', len(cnt), cnt)

train_examples = json.load(open('data/conala-renamed_funcs&docs/renamed_funcs_train.json'))
