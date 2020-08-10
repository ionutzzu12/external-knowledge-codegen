import json
import copy
import re

train_file = '../data/canonic_conala/canonic_conala_train.json'
test_file = '../data/canonic_conala/canonic_conala_test.json'
docs_file = '../data/canonic_conala/documentation.json'

mined_file = '../data/canonic_conala/canonic_conala_mined.jsonl'

def last_token(fname):
    return fname.split('.')[-1]


def canonicalize(fname):
    if fname[:2] == "a.":
        print('wtf')
    return fname.replace('.', '_')


def can_canonicalize(complete_name):
    return re.findall("dict\.|str\.|list\.", complete_name) == []


if __name__ == "__main__":



    train_data = json.load(open(train_file))
    test_data = json.load(open(test_file))
    docs_data = json.load(open(docs_file))
    new_docs = {}

    api_file = '../apidocs/processed/distsmpl/snippet_15k/goldmine_snippet_count100k_topk1_temp2.jsonl'
    api_data = [json.loads(jline) for jline in open(api_file).readlines()]

    new_api_data = []

    for ex in api_data:
        func_name = ex['snippet'].split('(')[0]

        if func_name in docs_data and can_canonicalize(func_name):
            ex['canonic'] = ex['snippet'].replace(func_name, canonicalize(func_name))
            d = {canonicalize(func_name): docs_data[func_name]['index']}
            ex['doc_id_by_name'] = d
            new_api_data.append(ex)
    json.dump(new_api_data, open('../data/canonic_conala_gut/renamed_funcs_apidocs.json', 'w'), indent=2)

    # TODO
    # for k, v in docs_data.items():
    #     if can_canonicalize(k):
    #         new_docs[canonicalize(k)] = v
    #     else:
    #         new_docs[last_token(k)] = v
    #
    # json.dump(new_docs, open('../data/canonic_conala_gut/renamed_funcs_docs.json', 'w'), indent=2)

    names_by_index = {d['index']: d['name'] for d in docs_data.values()}
    try:
        mined_data = json.load(open(mined_file))
    except:
        mined_data = [json.loads(jline) for jline in open(mined_file).readlines()]
    data = new_api_data

    for ex in data:
        # undoc += len(ex['undocumented_functions'])
        # if ex['undocumented_functions']:
        #     for u in ex['undocumented_functions']:
        #         undoc_set.add(u)

        ex['canonic'] = copy.copy(ex['snippet'])
        docs_id_by_canonic_name = {}

        for func in ex['functions']:
            found = 0
            for i in ex['function_ids']:
                complete_name = names_by_index[i]
                if last_token(func['name']) == last_token(complete_name):
                    assert complete_name in docs_data, complete_name
                    found += 1
                    new_func_name = canonicalize(complete_name)

                    if can_canonicalize(complete_name):
                        ex['canonic'] = ex['canonic'].replace(func['name'], new_func_name)
                        docs_id_by_canonic_name[new_func_name] = i
                    else:
                        docs_id_by_canonic_name[last_token(func['name'])] = i
                        print('NO')
                    assert names_by_index[i] == complete_name
            if found == 0:
                new_func_name = canonicalize(func['name'])
                ex['canonic'] = ex['canonic'].replace(func['name'], new_func_name)
            if found > 1:
                print('wow')
                docs_id_by_canonic_name = {}
            ex['doc_id_by_name'] = docs_id_by_canonic_name
        del ex['undocumented_functions']
        del ex['function_ids']
        del ex['function_set']
        del ex['functions']
        del ex['literals']
        del ex['operators']
        del ex['sketch']
        # ex['canonic'] = snippet
        # if total != found:
        #     print([f['name'] for f in ex['functions']], ex['undocumented_functions'], total, found)

    json.dump(data, open('../data/canonic_conala_gut/canonic_train.json', 'w'), indent=2)
    # json.dump(data, open('../data/canonic_conala_gut/renamed_funcs_mined.json', 'w'), indent=2)
    # print(undoc_set)
    # print(total1, found1, undoc)
    print('done')
