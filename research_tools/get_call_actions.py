import csv
import pickle
from asdl.transition_system import ApplyRuleAction, GenTokenAction
from collections import defaultdict
import matplotlib.pyplot as plt
import json


aliases = [('wxPython', 'wx'),
               ('PyGObject', 'gi'),
               ('tkinter', 'tk'),
               ('numpy', 'np'),
               ('pandas', 'pd'),
               ('matplotlib', 'plot'),
               ('matplotlib', 'plt'),
               ('matplotlib.pyplot', 'plot'),
               ('matplotlib.pyplot', 'plt'),
               ('networkx', 'nx'),
               ('tensorflow', 'tf'),
               ('opencv', 'cv2')
               ]

imports = [('sqlalchemy', 'session'),
           ('tkinter', 'root'),
           ('django', 'TemplateView'), ('django', 'models'), ('django', 'user'), ('django',  'session'),
           ('selenium', 'browser'),
           ('mechanize', 'br'),
           ('flask', 'session'),
           ('httplib', 'request'),
           ('pandas', 'df'), ('pandas', 'df1'), ('pandas', 'DataFrame'),
           ('tensorflow', 'session'),
           ('csv', 'writer'),
           ('Zipfile', 'archive'),
           ('zipfile', 'archive'),
           ('lxml', 'tree'),
           ('pillow', 'Image'),
           ('collections', 'ordereddict'),
           ('shutil', 'copy'),
           ('ast', 'lib'),
           ('argparse', 'parser'),
           ('re', 'sub'),
           ]


def invalid_module(token):
    return 'str_' == token[:4] or 'var_' == token[:4] or len(token) <= 1 or token == 'file'


def compute_categ_dict(data):
    golds = []

    gen_token = "GenToken"
    possible = {1: ['Call', 'Attribute', 'Str', gen_token, gen_token],
                2: ['Call', 'Attribute', 'Name', gen_token, gen_token],
                3: ['Call', 'Attribute', 'Attribute', 'Name', gen_token, gen_token, gen_token],
                4: ['Call', 'Name', gen_token],
                # 5: ['Attribute', 'Str', gen_token, gen_token],
                6: ['Attribute', 'Name', gen_token, gen_token],
                7: ['Attribute', 'Attribute', 'Name', gen_token, gen_token, gen_token]
                }

    def get_tokens(desired_seq, actual_seq):
        tokens = []

        for index, action_info in enumerate(actual_seq):
            if index >= len(desired_seq):
                break
            op_name = desired_seq[index]

            if op_name == gen_token:
                if isinstance(action_info.action, GenTokenAction):
                    tokens.append(action_info.action.token)
                else:
                    return None
            else:
                assert isinstance(action_info.action, ApplyRuleAction)
                if action_info.action.production.constructor.name != op_name:
                    return None
        return tokens

    for ex in data:
        actions = ex.tgt_actions
        n = 8
        last_n = []
        countdown = -1

        for a in actions:
            if isinstance(a.action, ApplyRuleAction) and a.action.production.constructor.name == 'Call':
                countdown = n
                last_n = []
            if last_n == [] and isinstance(a.action,
                                           ApplyRuleAction) and a.action.production.constructor.name == 'Attribute':
                countdown = n
                last_n = []
            if countdown > -1:
                countdown -= 1
                last_n.append(a)
            if countdown == 0:
                golds.append((last_n, ex))

    gold_tokens = []
    calls_list = []

    for seq, ex in golds:
        results = {}
        for premise_id in possible:
            desired_seq = possible[premise_id]
            result = get_tokens(desired_seq, seq)
            if result is None:
                # print(seq)
                pass
            else:
                results[premise_id] = result
                calls_list.append((result, ex))

        if results == {}:
            # print(seq)
            # print(code)
            continue
        # if 3 in results:  # or 6 in results or 5 in results:
        #     # print(results)
        #     # print(code)
        #     code = code

        gold_tokens.append(results)

    # _3s = [g for g in gold_tokens if 7 in g]
    # print(_3s)
    # print(gold_tokens)

    per_module_dict = defaultdict(list)

    # examples_idx = {ex: i for i, ex in enumerate(data)}
    new_data = [example.meta['example_dict'] for example in data]
    for d in new_data:
        d['functions'] = []

    for tokens, example in calls_list:
        if invalid_module(tokens[0]):
            tokens = tokens[1:]

        if tokens:
            func_name = '.'.join(tokens)
            crt_dict = example.meta['example_dict']

            crt_dict['functions'].append(func_name)

        if len(tokens) == 1:
            per_module_dict["no_module"].append(tokens[0])
        elif len(tokens) == 2:
            module = tokens[0]
            func = tokens[1]
            per_module_dict[module].append(func)
        elif len(tokens) == 3:
            module = tokens[0]
            submodule = tokens[1]
            func = tokens[2]
            per_module_dict[module].append((submodule, func))
        else:
            pass

    # print(per_module_dict)
    per_category_dict = {}
    categ_by_module = {}

    def basic_stats_dict():
        return {'_total': 0}

    with open('data/conala/module_names.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        last_categ = ''

        for row in csv_reader:
            # print(f'\trow elems: {row}')
            line_count += 1

            if len(row) == 2:
                assert row[0] == '0'
                last_categ = row[1]
                per_category_dict[last_categ] = basic_stats_dict()

            if len(row) == 1:
                per_category_dict[last_categ][row[0]] = {}
                categ_by_module[row[0]] = last_categ

        # print(f'Processed {line_count} lines.')

    # print(per_category_dict)

    per_category_dict['outliers'] = basic_stats_dict()

    for module, calls in per_module_dict.items():
        for call in calls:
            if module in categ_by_module:
                categ = categ_by_module[module]
                my_d = per_category_dict[categ][module]
            else:
                categ = 'outliers'
                my_d = per_category_dict['outliers']
            if call in my_d:
                my_d[call] += 1
            else:
                my_d[call] = 1
            per_category_dict[categ]['_total'] += 1

    # print(per_category_dict)
    return per_category_dict, new_data


def find_function_by_name(func_name, functions_by_name):
    keys = set(functions_by_name.keys())
    head = func_name.split('.')[0]
    tail = '.'.join(func_name.split('.')[1:])

    if func_name in keys:
        return functions_by_name[func_name]
    elif head == 'datetime' and ('datetime.' + func_name) in keys:
        return functions_by_name['datetime.' + func_name]
    elif (head == 'cur' or head == 'cursor' or head == "Cursor") and tail != '' and 'sqlite3.Cursor.' + tail in keys:
        return functions_by_name['sqlite3.Cursor.' + tail]
    elif (head == 'cur' or head == 'cursor' or head == "Cursor") and tail == '' and 'sqlite3.Cursor' in keys:
        return functions_by_name['sqlite3.Cursor']
    else:
        for module, alias in aliases:
            if head == alias and module + '.' + tail in keys:
                return functions_by_name[module + '.' + tail]

        for module, imported in imports:
            if head == imported and module + '.' + func_name in keys:
                return functions_by_name[module + '.' + func_name]

        return None


def not_found_funcs():
    not_found_funcs = {}

    train_json = json.load(open("data/annotated_train_set.json", 'r'))
    dev_json = json.load(open("data/annotated_dev_set.json", 'r'))
    test_json = json.load(open("data/annotated_test_set.json", 'r'))

    total = 0
    not_found = 0

    for _data in [train_json, dev_json, test_json]:
        for ex in _data:
            for index, func_id in enumerate(ex['functions_ids']):
                total += 1
                if not func_id:
                    not_found += 1

                    k = ex['functions'][index]
                    if k in not_found_funcs:
                        not_found_funcs[k] += 1
                    else:
                        not_found_funcs[k] = 1

    print(total, not_found, len(not_found_funcs))
    # json.dump(not_found_funcs, open("data/not_found_functions.json", 'w'), indent=2)


if __name__ == "__main__":
    not_found_funcs()

    train_data = pickle.load(open("data/conala/train.gold.full.bin", 'rb'))
    dev_data = pickle.load(open("data/conala/dev.bin", 'rb'))
    test_data = pickle.load(open("data/conala/test.bin", 'rb'))
    mined_data = pickle.load(open("data/conala/mined_100000.bin", 'rb'))
    a, a_data = compute_categ_dict(train_data)
    b, b_data = compute_categ_dict(dev_data)
    c, c_data = compute_categ_dict(test_data)
    d, d_data = compute_categ_dict(mined_data)

    functions_file = "data/conala/python-docs-new3.jsonl"

    try:
        func_set = json.load(open(functions_file))
    except:
        func_set = [json.loads(jline) for jline in open(functions_file).readlines()]

    # print(func_set)
    # functions_by_name = {}
    # for f in func_set:
    #     functions_by_name[f['name']] = f['index']

    # fids = 'functions_ids'
    # for id, ex in enumerate(b_data):
    #     ex[fids] = []
    #     for func_name in ex['functions']:
    #         ex[fids].append(find_function_by_name(func_name, functions_by_name))
    #
    # print(c_data)

    # json.dump(b_data, open("data/annotated_dev_set.json", "w"), indent=4)
    # json.dump(func_set, open("data/functions_details.json", "w"), indent=4)

    # final_dicts = [a, b, c]
    # lengths = [len(train_data), len(dev_data), len(test_data)]

    # final_dicts = [a, d]
    # lengths = [len(train_data), len(mined_data)]
    #
    # stats = [[], [], []]
    # xs = [[], [], []]
    # categ_names = []
    #
    # for categ in a.keys():
    #     for i in range(len(final_dicts)):
    #         stats[i].append(final_dicts[i][categ]['_total'] / lengths[i])
    #     categ_names.append(categ)
    #
    # n = len(a.keys())
    #
    # for i in range(len(final_dicts)):
    #     for j in range(n):
    #         xs[i].append(j * 3 + i)
    #
    #     plt.bar(xs[i], stats[i], align='center')
    #
    # plt.xticks(xs[1], categ_names, rotation='40', fontsize=10)
    # # plt.title('Per Question Type Accuracy', fontsize=10)
    # # plt.xlabel('Question Types', fontsize=10)
    # # plt.ylabel('Accuracy', fontsize=10)
    # plt.legend(labels=['train', 'dev', 'test'])
    # plt.show()
