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


def get_docs():
    data = json.load(open('data/conala_new/train_doc.json')) + json.load(open('data/conala_new/test_doc.json'))
    # sep = '<sep>'
    type_sep = '<type>'
    param_mandatory = '<param_mandatory>'
    param_optional = '<param_optional>'

    res_funcs = {}

    cnt = set()
    for e in data:
        if 'functions' in e:
            for f in e['functions']:
                name = f['module'] + '.' + f['name'] if f['module'] not in ['built-in', 'stdtypes'] else f['name']
                key = canonic_fname(name)

                # description = []
                # for s in f['description']:
                #     description += tokenize_intent(s)

                encoded_func = [f['return_type']['name'], f['is_method']] + f['description'].split(' ')

                encoded_func2 = encoded_func
                for param in f['parameters']:
                    encoded_func2 += [param_mandatory, param['name']] + tokenize_intent(param['description'])
                    # encoded_func2 += [sep, param['name'], param['types'][0]['name']] + [mandatory]
                    for type in param['types']:
                        encoded_func2 += [type_sep, type['name']] + type['description'].split(' ')

                encoded_func3 = encoded_func2
                for param in f['optional_parameters']:
                    encoded_func3 += [param_optional, param['name'], param['types'][0]['name']] + tokenize_intent(param['description'])
                    # encoded_func3 += [sep, param['name'], param['types'][0]['name']] + [optional]
                    for type in param['types']:
                        encoded_func2 += [type_sep, type['name']] + type['description'].split(' ')

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

    # json.dump(res_funcs, open('data/conala_new/revised_docs.json', 'w'), indent=2)
    # print('done', len(cnt), cnt)
    return res_funcs


def get_params():
    data = json.load(open('data/conala_new/train_doc.json')) + json.load(open('data/conala_new/test_doc.json'))
    params = {}
    optional_params = {}

    for e in data:
        if 'functions' in e:
            for f in e['functions']:
                name = f['module'] + '.' + f['name'] if f['module'] not in ['built-in', 'stdtypes'] else f['name']
                key = canonic_fname(name)

                params[key] = f['parameters']
                optional_params[key] = f['optional_parameters']
    return params, optional_params


import subprocess
import pickle

if __name__ == "__main__":


    # data = json.load(open('data/conala_new/test_doc.json'))
    data = pickle.load(open('data/conala_new/test-types_for_mypy.bin', 'rb'))

    filtered_data = []

    intro = """
    from typing import *
    
    myList = []  # type: List
    str_0 = ''  # type: str
    
    """

    all_exs = []
    my_file = open("complete_local_vars.txt", "w")

    for i, e in enumerate(data):
        ok = True
        # for f in e['functions']:
        #     if f['module'] not in ['built-in', 'stdtypes', 'dict', 'str']:
        #         ok = False
        #         break

        if ok:
            # add local vars
            local_vars = {}
            for var_name in e.meta['slot_map']:
                if var_name in e.src_sent:
                    sent_idx = e.src_sent.index(var_name)
                    local_vars[var_name] = e.src_sent[sent_idx - 1]

            try:
                my_file.write('<< ' + ' '.join(e.src_sent) + '\n')
                my_file.write('<< ' + e.tgt_code + '\n')

                for var, type in local_vars.items():
                    all_exs.append((var, type))
                    line = ''

                    if type == 'list':
                        line = var + ' = []  # type: List'
                    elif type == 'dictionary':
                        line = var + ' = {}  # type: dict'
                    elif type == 'tuple':
                        line = var + ' = (1,)  # type: tuple'
                    elif type == 'string':
                        line = var + ' = ""  # type: str'
                    elif type == 'strings':
                        line = var + ' = ""  # type: str'
                    elif type == 'character':
                        line = var + ' = ""  # type: chr'

                    elif type == 'number':
                        line = var + ' = 1  # type: int'
                    elif type == 'index':
                        line = var + ' = 1  # type: int'
                    elif type == 'int':
                        line = var + ' = 1  # type: int'
                    elif type == 'integer':
                        line = var + ' = 1  # type: int'

                    if line: my_file.write(line + '\n')
                my_file.write('\n')

                # f = open("my_py_tst.py", "w")
                # f.write(intro + e.tgt_code)
                # f.close()
                # output = subprocess.check_output(['mypy', '--py2', 'my_py_tst.py'])
                # assert output[:7] == b'Success'

                filtered_data.append(e)
            except:
                pass


    print('done')
    # json.dump(filtered_data, open('data/conala_new/test-types_for_mypy.json', 'w'))

