import pickle
import numpy as np
# from ...components.evaluator import Evaluator
from run import *
from exp import main

import json
import numpy as np
import string
from operator import itemgetter
import matplotlib.pyplot as plt


def test_on_api_docs():
    test_args = TestArgs('t5-funcs25-renamed_fs-patience7-renamed_bleu_metric-last_cell-just_train_set_fs')
    # test_args = TestArgs('t4-funcs25-renamed_fs-patience7-renamed_bleu_metric-last_cell')
    # test_args = TestArgs('t3-funcs15-renamed_fs-patience7-renamed_bleu_metric-last_state')
    # test_args = TestArgs('t2-funcs5-renamed_fs-patience5-renamed_bleu_metric-last_state')
    # test_args = TestArgs('t1-funcs10-renamed_fs-patience10-renamed_bleu_metric')
    # test_args = TestArgs('t0-funcs-renamed_fs-patience15-renamed_bleu_metric')
    # test_args = TestArgs('funcs_train-dev200-no_limits')
    # test_args = TestArgs('classic_train-dev200-no_limits_at_all')
    # test_args.test_file = 'data/conala-renamed_funcs&docs/renamed_funcs_apidocs.bin'
    # test_args.save_decode_to = False  # f'decodes/conala/apidocs_test-funcs_train-dev200-no_limits.test.decode'
    main(test_args)


def sort_funcs_in_train_set():
    just_train_set = True
    train_raw_list = json.load(open('data/conala-renamed_funcs&docs/renamed_funcs_train.json'))
    funcs_field = 'doc_id_by_name'

    train_set = {}
    if just_train_set:
        for example in train_raw_list:
            if funcs_field in example:
                doc_id_by_name = example[funcs_field]
                for key in doc_id_by_name:
                    if key in train_set:
                        train_set[key] += 1
                    else:
                        train_set[key] = 1

    print(sorted(train_set.items(), key=itemgetter(1), reverse=True)[:25])


if __name__ == '__main__':
    # decode_results = pickle.load(open('decodes/conala/classic_train-dev200-no_limits.test.decode', 'rb'))
    # dev_examples = pickle.load(open('data/conala-renamed_funcs&docs/dev.bin', 'rb'))
    # test_examples = pickle.load(open('data/conala-renamed_funcs&docs/test.bin', 'rb'))
    # print('done')
    '''
    test_on_api_docs()
    sort_funcs_in_train_set
    
    '''
    results = {}

    results_file = 'test_results.txt'
    with open(results_file) as f:
        name = None
        all_metrics_combined = None

        for line in f.readlines():
            # print(line)
            if line[0] == '#':
                if all_metrics_combined and len(all_metrics_combined) == 18:
                    results[name]['all_metrics'] = all_metrics_combined

                # print('name: %s' % line[1:-1])
                name = line.strip(string.punctuation).strip(string.whitespace)
                results[name] = {}
                all_metrics_combined = []
            elif ':' in line:
                tokens = line.split(':')
                # print('metric - %s: %f' % (tokens[0], float(tokens[1])))
                results[name][tokens[0].strip(string.punctuation).strip(string.whitespace)] = float(tokens[1])
                all_metrics_combined.append(float(tokens[1]))

    # items = [pair for pair in results.items() if 'all_metrics' in pair[1]]
    # x = [values['all_metrics'] for _, values in items]
    # y = [1 if 'last_cell' in key else 0 for key, values in items]
    # method_names = [i for i in enumerate([key for key, _ in items])]
    #
    # x2 = [x[0][:]]
    #
    # # names2 = []
    # for _ in range(5):
    #     last = x2[-1][:]
    #     last[4] *= 1.4
    #     x2.append(last)
    #
    # print(x2)
    # # print(method_names)
    #
    # x = np.array(x)
    # y = np.array(y)
    #
    # # print(results)
    #
    # from sklearn.decomposition import PCA
    #
    # pca = PCA(n_components=2)
    # principalComponents = pca.fit_transform(x)
    # # principalDf = pd.DataFrame(data=principalComponents
    # #                            , columns=['principal component 1', 'principal component 2'])
    #
    # principalComponents2 = pca.transform(np.array(x2))
    #
    # fig = plt.figure(figsize=(8, 8))
    # ax = fig.add_subplot(1, 1, 1)
    # ax.set_xlabel('Principal Component 1', fontsize=15)
    # ax.set_ylabel('Principal Component 2', fontsize=15)
    # ax.set_title('2 component PCA', fontsize=20)
    # targets = [1, 0]
    # colors = ['r', 'b']
    #
    # print(principalComponents.shape, principalComponents)
    # print(y.shape, y)
    # print(principalComponents2.shape, principalComponents2)
    #
    # # principalComponents = x[:, (0, 6)]
    #
    # for target, color in zip(targets, colors):
    #     indicesToKeep = y == target
    #     ax.scatter(principalComponents[indicesToKeep][:, 0]
    #                , principalComponents[indicesToKeep][:, 1]
    #                , c=color
    #                , s=50)
    #
    # for i in range(principalComponents2.shape[0]):
    #     principalComponent = principalComponents2[i]
    #     ax.scatter(principalComponent[0]
    #                , principalComponent[1]
    #                , c='g'
    #                , s=50)
    #
    # for idx, name in method_names:
    #     ax.annotate('bleu_%.2f_' % (x[idx][0]) + name, (principalComponents[idx][0], principalComponents[idx][1]))
    #
    # ax.legend(targets)
    # ax.grid()
    # plt.show()
    #
    # print(pca.explained_variance_ratio_)
    # print(pca.components_)

    print(results)
    metrics = [k for k, v in results['classic train, patience = 5'].items()]
    corpus_bleu = metrics[0]
    others = metrics[1:]

    fig = plt.figure()
    for i, metric in enumerate(others):
        if metric == 'all_metrics': continue
        ax = fig.add_subplot(3, 6, i+2)
        for method, values in results.items():
            # if 'apidocs' in method:
            #     continue
            x = values[corpus_bleu]
            if metric in values:
                y = values[metric]
                plt.scatter(x, y, s=50, label=method)
                # plt.annotate(method, (x, y))
        # plt.set_xlabel('corpus bleu', fontsize=15)
        # plt.set_ylabel(metric, fontsize=15)
        ax.set_title(metric, fontsize=8)
    # fig.legend()point
    plt.show()

