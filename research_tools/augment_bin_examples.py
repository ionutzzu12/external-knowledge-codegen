import pickle
import json
from components.dataset import Example
import nltk
from numpy.random import choice
from operator import itemgetter


# examples_bin_file = "../data/conala/train.gold.full.bin"
# examples_json_file = "../data/annotated_train_set.json"
examples_bin_file = "../data/conala/dev.bin"
examples_json_file = "../data/annotated_dev_set.json"
functions_file = "../data/functions_details.json"
NUM_MULTICHOICE = 10


def tokenize_intent(intent):
    lower_intent = intent.lower()
    tokens = nltk.word_tokenize(lower_intent)
    return tokens


def get_single_token_functions_ids(func_set):
    ret = []
    # total = 0
    # opcode = 0

    for f in func_set:
        if '.' not in f['name'] and f['module'] != '2to3' and "opcode" not in f['name']:
            ret += [f['index']]
    # print('total', total)
    # print('opcode', opcode)
    return ret


if __name__ == "__main__":
    data = pickle.load(open(examples_bin_file, 'rb'))
    annot_set = json.load(open(examples_json_file))
    func_set = json.load(open(functions_file))
    sglf_ids = get_single_token_functions_ids(func_set)

    func_counts = {}
    for index, example in enumerate(data):
        assert example.meta['example_dict']['question_id'] == annot_set[index]['question_id']

        crt_functions = [{'fid': j, 'fname': i} for i, j in
                         zip(annot_set[index]['functions'], annot_set[index]['functions_ids'])]
        for fdict in crt_functions:
            if fdict['fid'] is not None and '.' not in fdict['fname']:
                fid = fdict['fid']
                if fid in func_counts:
                    func_counts[fid] += 1
                else:
                    func_counts[fid] = 1

    sorted_funcs = []
    common_single_f_ids = []
    for fid, cnt in sorted(func_counts.items(), key=itemgetter(1), reverse=True):
        sorted_funcs.append({(fid, func_set[fid]['name'], cnt)})
        common_single_f_ids.append(fid)

    new_data = []
    for index, example in enumerate(data):
        assert example.meta['example_dict']['question_id'] == annot_set[index]['question_id']

        new_ex = Example(example.src_sent, example.tgt_actions, example.tgt_code, example.tgt_ast, example.idx, example.meta)
        crt_functions = [{'fid': j, 'fname': i} for i, j in zip(annot_set[index]['functions'], annot_set[index]['functions_ids'])]
        new_data.append(new_ex)

        valid_functions_ids = []

        for fdict in crt_functions:  # select sample (python internal) functions
            if fdict['fid'] is not None and '.' not in fdict['fname']:
                valid_functions_ids.append(fdict['fid'])
                # f_details = sglf[fdict['fid']]
                # assert f_details['index'] == fdict['fid']
                # fdict['doc'] = tokenize_intent(''.join(f_details['doc']))
                # valid_functions.append(fdict)
                fid = fdict['fid']
                if fid in func_counts:
                    func_counts[fid] += 1
                else:
                    func_counts[fid] = 1

        valid_functions_ids_chosen = choice(common_single_f_ids, NUM_MULTICHOICE - len(valid_functions_ids))
        valid_functions_ids += list(valid_functions_ids_chosen)
        valid_functions = []
        for id in valid_functions_ids:
            f_details = func_set[id]
            assert f_details['index'] == id
            fdict = {'fname': f_details['name'], 'fid': id, 'doc': tokenize_intent(''.join(f_details['doc']))}
            valid_functions.append(fdict)

        new_ex.functions = valid_functions

    pickle.dump(new_data, open("../data/conala/added_funcs_dev.bin", 'wb'))
