# coding=utf-8
from __future__ import print_function

import sys
import traceback
from tqdm import tqdm
import subprocess


def decode(examples, model, args, verbose=False, **kwargs):
    ## TODO: create decoder for each dataset

    if verbose:
        print('evaluating %d examples' % len(examples))

    was_training = model.training
    model.eval()

    decode_results = []
    count = 0
    for example in tqdm(examples, desc='Decoding', file=sys.stdout, total=len(examples)):
        functions_to_filter = example.functions if hasattr(example, "functions") else None
        local_vars_to_filter = example.local_vars if hasattr(example, "local_vars") else None
        hyps = model.parse(example.src_sent, context=None, beam_size=args.beam_size, functions=functions_to_filter, local_vars=local_vars_to_filter)
        decoded_hyps = hyps  # FIXME this is modified

        # for hyp_id, hyp in enumerate(hyps):
            # got_code = False
            # try:
            #     hyp.code = model.transition_system.ast_to_surface_code(hyp.tree)
            #     # got_code = True
            #     # print('\n<<< ', hyp.code)
            #
            #     f = open("my_py_tst.py", "w")
            #     f.write(hyp.code)
            #     f.close()
            #     output = subprocess.check_output(['mypy', '--py2', 'my_py_tst.py'])
            #     assert output[:7] == b'Success'
            #     decoded_hyps.append(hyp)
            #
            # except subprocess.CalledProcessError as e:
            #     print(str(e))
            # except:
            #     if verbose:
            #         print("Exception in converting tree to code:", file=sys.stdout)
            #         print('-' * 60, file=sys.stdout)
            #         print('Example: %s\nIntent: %s\nTarget Code:\n%s\nHypothesis[%d]:\n%s' % (example.idx,
            #                                                                                  ' '.join(example.src_sent),
            #                                                                                  example.tgt_code,
            #                                                                                  hyp_id,
            #                                                                                  hyp.tree.to_string()), file=sys.stdout)
            #         # if got_code:
            #         #     print()
            #         #     print(hyp.code)
            #         traceback.print_exc(file=sys.stdout)
            #         print('-' * 60, file=sys.stdout)

        count += 1

        decode_results.append(decoded_hyps)
        # print('\n', len(decoded_hyps))

    if was_training:
        model.train()

    return decode_results


def evaluate(examples, parser, evaluator, args, verbose=False, return_decode_result=False, eval_top_pred_only=False):
    # if len(examples) > 500:
    #     from random import shuffle, seed
    #     seed(1)
    #     shuffle(examples)
    #     examples = examples[:500]  # FIXME: for debug

    decode_results = decode(examples, parser, args, verbose=verbose)

    eval_result = evaluator.evaluate_dataset(examples, decode_results, fast_mode=eval_top_pred_only, args=args)

    if return_decode_result:
        return eval_result, decode_results
    else:
        return eval_result
