from datasets.conala.util import tokenize_intent
from operator import itemgetter

import json
import time


def load_docs(just_train_set=False, top_popular=None):
    print('loading docs... just_train_set =', just_train_set)
    start_time = time.time()
    docs_raw_dict = json.load(open('../data/conala-renamed_funcs&docs/renamed_funcs_docs.json'))
    train_raw_list = json.load(open('../data/conala-renamed_funcs&docs/renamed_funcs_train.json'))
    funcs_field = 'doc_id_by_name'

    train_set_count = {}
    train_set = set()
    if just_train_set:
        for example in train_raw_list:
            if funcs_field in example:
                doc_id_by_name = example[funcs_field]
                for key in doc_id_by_name:
                    train_set.add(key)

                    if key in train_set_count:
                        train_set_count[key] += 1
                    else:
                        train_set_count[key] = 1

    if not top_popular:
        chosen_func_set = train_set
    else:
        sorted_tuples = sorted(train_set_count.items(), key=itemgetter(1), reverse=True)[:top_popular]
        chosen_func_set = set([fname for fname, _ in sorted_tuples])

    # docs_index_dict = {}
    # for key, value in docs_raw_dict.items():
    #     docs_index_dict[value['index']] = tokenize_intent(' '.join(value['doc'][:2]))docs_index_dict = {}
    canonic_to_orig_names = {}
    docs_dict = {}
    func_names = []

    docs_raw_dict_filtered = {}

    for key, value in docs_raw_dict.items():
        if just_train_set and key not in chosen_func_set:
            continue
        docs_raw_dict_filtered[key] = value

        doc = value['doc']

        if isinstance(doc, str):
            docs_dict[key] = tokenize_intent(doc)
        else:
            docs_dict[key] = tokenize_intent(' '.join(doc[:2]))
        func_names.append(key)
        canonic_to_orig_names[key] = value['name']

    print('done! total:%d, chosen_func_set:%d, took %ds' % (len(docs_raw_dict), len(chosen_func_set), time.time() - start_time))
    return docs_raw_dict_filtered, docs_dict, func_names, canonic_to_orig_names


if __name__ == "__main__":
    docs_raw_dict_filtered, docs_dict, func_names, canonic_to_orig_names = load_docs(just_train_set=True)

    fs_by_module = {}
    for k, v in docs_raw_dict_filtered.items():
        m = v['module']
        if m not in fs_by_module:
            fs_by_module[m] = [v]
        else:
            fs_by_module[m].append(v)

    module = 're'
    for f in fs_by_module[module]:
        # print(f['name'], f['doc'])
        print('.'.join(f['name'].split('.')[1:]))
        # print(' '.join(f['doc']))  # print(f['doc'])
        pass

    result = sorted(fs_by_module.items(), reverse=True, key=lambda item: len(item[1]))

    # for k in result:
    #     print(k[0])

    used_modules = [f[0] for f in result[:14]]
    docs_raw_dict = json.load(open('../data/conala-renamed_funcs&docs/renamed_funcs_docs.json'))
    train_raw_list = json.load(open('../data/conala-renamed_funcs&docs/renamed_funcs_train.json'))
    valid_train_examples = []

    all_num = len(train_raw_list)
    docum_num = 0
    ingested_num = 0

    for e in train_raw_list:
        docum = True
        ingest = True
        if 'doc_id_by_name' in e:
            for func_name in e['doc_id_by_name']:
                if func_name in docs_raw_dict:
                    # docum_num += 1
                    if docs_raw_dict[func_name]["module"] in used_modules:
                        # ingested_num += 1
                        pass
                    else:
                        ingest = False
                else:
                    docum = ingest = False
        else:
            docum = ingest = False
        if docum: docum_num += 1
        if ingest: ingested_num += 1

    print('done')
