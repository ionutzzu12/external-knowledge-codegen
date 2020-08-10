import csv
import json
import ast
import re
from operator import itemgetter
from matplotlib import pyplot as plt


class Function:
    def __init__(self, id, module, name, return_type, parameters, description, object, mutable):
        self.id = int(id)
        self.module = module
        self.name = name
        self.return_type = return_type
        if parameters == '':
            self.parameters = []
        else:
            self.parameters = ast.literal_eval(parameters)
            if not isinstance(self.parameters, list):
                self.parameters = [self.parameters]

        self.description = description
        self.object_name = None if object == '' else object
        self.mutable = mutable == "TRUE"

    def __str__(self):
        return self.name


class Parameter:
    def __init__(self, id, name, types, description):
        self.id = int(id)
        self.name = name
        types_strings = re.split("[ ,\[\]]", types)
        self.types = []
        for t in types_strings:
            if t != '':
                self.types.append(t)
        self.description = description

    def __str__(self):
        return self.name


class Type:
    def __init__(self, id, name, description):
        self.id = int(id)
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


def ingest_objects(csv_file_path, constr):
    csv_file = open(csv_file_path, 'r', encoding='utf-8')

    reader = csv.reader(csv_file)
    headers = next(reader, None)
    dict_reader = csv.DictReader(csv_file, headers)

    obj_list = []
    obj_by_id = {}

    for f in dict_reader:
        if f['id']:
            try:
                new_f = constr(f)
                obj_list.append(new_f)
                obj_by_id[int(f['id'])] = new_f
            except Exception as e:
                print(e)
                pass

    return obj_list, obj_by_id


funcs, funcs_by_id = ingest_objects('data/codegen func documentation/CodeGen Function Documentation Python - Functions.csv',
                       lambda f: Function(f['id'],
                                          f['Module/Built-in class'],
                                          f['Name'],
                                          f['Return Type'],
                                          f['Parameters'],
                                          f['Description'],
                                          f['Object method'],
                                          f['Mutable']))

params, params_by_id = ingest_objects('data/codegen func documentation/CodeGen Function Documentation Python - Parameters.csv',
                       lambda f: Parameter(f['id'],
                                          f['Name'],
                                          f['Type'],
                                          f['Description']))

types, types_by_id = ingest_objects('data/codegen func documentation/CodeGen Function Documentation Python - Types.csv',
                       lambda f: Type(f['id'],
                                          f['Type'],
                                          f['Description']))

for f in funcs:
    updated_params = []
    for p in f.parameters:
        updated_params.append(params_by_id[p])
    f.parameters = updated_params

for p in params:
    updated_types = []
    for t in p.types:
        matches = re.findall('\d+|\*+', t)
        updated_types.append(types_by_id[int(matches[0])])
    p.types = updated_types

compatible_types_dict = {
    'iterable': ['collection', 'sequence'],
    'collection': ['dictionary'],
    'sequence': ['list', 'tuple', 'dataframe', 'string'],
    'number': ['integer', 'float', 'complex'],
    'integer': ['bool'],
    'string': ['path', 'regex'],
    'object': ['function', 'code', 'iterable', 'type', 'iterator', 'file', 'command', 'condition']
    }


def get_all_compatible_types(type_name):
    ret = [type_name]
    search_id = 0

    while search_id < len(ret):
        if ret[search_id] in compatible_types_dict:
            ret += compatible_types_dict[ret[search_id]]
        search_id += 1

    assert len(ret) == len(set(ret))
    return ret


def get_all_funcs_compatible_with_type(tname):  # TODO 'object' is compatible with all other objects
    all_compatible_types = get_all_compatible_types(tname)
    # print(tname, all_compatible_types)

    res = []
    for type_name in all_compatible_types:
        if type_name in funcs_by_return_type:
            res += funcs_by_return_type[type_name]
    # print(len(res), res)
    return res


funcs_by_return_type = {}

for func in funcs:
    ret_type = func.return_type

    if ret_type in funcs_by_return_type:
        funcs_by_return_type[ret_type].append(func.name)
    else:
        funcs_by_return_type[ret_type] = [func.name]


for type in types:
    tname = type.name
    res = get_all_funcs_compatible_with_type(tname)

    print(tname, len(res), res)


data = json.load(open("data/codegen func documentation/train_doc.json"))

return_types_freq = {}

for e in data:
    if 'functions' in e:
        for f in e['functions']:
            type = f['return_type']['name']
            if type in return_types_freq:
                return_types_freq[type] += 1
            else:
                return_types_freq[type] = 1

items = [(k, v, len(get_all_funcs_compatible_with_type(k))) for k, v in sorted(return_types_freq.items(), key=lambda item: item[1], reverse=True)]

y = [item[1] for item in items]
z = [item[2] for item in items]
n = [item[0] for item in items]

fig, ax = plt.subplots()
ax.scatter(z, y)
ax.set_xlabel('compatible funcs')
ax.set_ylabel('frequency')

for i, txt in enumerate(n):
    ax.text(z[i], y[i], txt, size=5)

plt.show()


print('done')
