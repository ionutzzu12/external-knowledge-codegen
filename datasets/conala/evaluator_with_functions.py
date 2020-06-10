import csv

from components.evaluator import Evaluator
from common.registerable import Registrable
from components.dataset import Dataset
from .util import decanonicalize_code
from .conala_eval import tokenize_for_bleu_eval
from .bleu_score import compute_bleu
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import numpy as np
import ast
import astor

from research_tools.parser_by_radu import Parser
from components.dataset import load_docs
import re


@Registrable.register('conala_functions_evaluator')
class ConalaFunctionsEvaluator(Evaluator):
    def __init__(self, transition_system=None, args=None):
        super(ConalaFunctionsEvaluator, self).__init__()
        self.transition_system = transition_system
        # self.default_metric = 'corpus_bleu'
        self.default_metric = 'renamed_funcs_corpus_bleu'

    def is_hyp_correct(self, example, hyp):
        ref_code = example.tgt_code
        ref_py_ast = ast.parse(ref_code)
        ref_reformatted_code = astor.to_source(ref_py_ast).strip()

        ref_code_tokens = self.transition_system.tokenize_code(ref_reformatted_code)
        hyp_code_tokens = self.transition_system.tokenize_code(hyp.code)

        return ref_code_tokens == hyp_code_tokens

    # def get_sentence_bleu(self, example, hyp):
    #     return sentence_bleu([tokenize_for_bleu_eval(example.meta['example_dict']['snippet'])],
    #                          tokenize_for_bleu_eval(hyp.decanonical_code),
    #                          smoothing_function=SmoothingFunction().method3)
    #
    # def get_sentence_bleu_f(self, example, hyp):
    #     return sentence_bleu([tokenize_for_bleu_eval(example.meta['example_dict']['canonic'])],
    #                          tokenize_for_bleu_eval(hyp.decanonical_code),
    #                          smoothing_function=SmoothingFunction().method3)

    def evaluate_dataset_helper(self, examples, decode_results, output_plaintext_file_name):
        output_plaintext_file = None
        if output_plaintext_file_name:
            output_plaintext_file = open(output_plaintext_file_name + '.txt', 'w', encoding='utf-8')

        tokenized_ref_snippets = []
        hyp_code_tokens = []
        best_hyp_code_tokens = []
        sm_func = SmoothingFunction().method3
        sent_bleu_scores = []
        oracle_bleu_scores = []
        oracle_exact_match = []
        for example, hyp_list in zip(examples, decode_results):
            tokenized_ref_snippets.append(example.reference_code_tokens)
            example_hyp_bleu_scores = []
            if hyp_list:
                for i, hyp in enumerate(hyp_list):
                    hyp.bleu_score = sentence_bleu([example.reference_code_tokens],
                                                   hyp.decanonical_code_tokens,
                                                   smoothing_function=sm_func)
                    hyp.is_correct = self.is_hyp_correct(example, hyp) or \
                        example.reference_code_tokens == hyp.decanonical_code_tokens

                    example_hyp_bleu_scores.append(hyp.bleu_score)

                top_decanonical_code_tokens = hyp_list[0].decanonical_code_tokens
                sent_bleu_score = hyp_list[0].bleu_score
                best_hyp_idx = np.argmax(example_hyp_bleu_scores)
                oracle_sent_bleu = example_hyp_bleu_scores[best_hyp_idx]
                _best_hyp_code_tokens = hyp_list[best_hyp_idx].decanonical_code_tokens
            else:
                top_decanonical_code_tokens = []
                sent_bleu_score = 0.
                oracle_sent_bleu = 0.
                _best_hyp_code_tokens = []

            # write results to file
            if output_plaintext_file:
                output_plaintext_file.write('>>> gen: ' + " ".join(top_decanonical_code_tokens) + '\n' +
                                            '>>> ref: ' + " ".join(example.reference_code_tokens) + '\n\n')
            oracle_exact_match.append(any(hyp.is_correct for hyp in hyp_list))
            hyp_code_tokens.append(top_decanonical_code_tokens)
            sent_bleu_scores.append(sent_bleu_score)
            oracle_bleu_scores.append(oracle_sent_bleu)
            best_hyp_code_tokens.append(_best_hyp_code_tokens)

        bleu_tup = compute_bleu([[x] for x in tokenized_ref_snippets], hyp_code_tokens, smooth=False)
        corpus_bleu = bleu_tup[0]

        bleu_tup = compute_bleu([[x] for x in tokenized_ref_snippets], best_hyp_code_tokens, smooth=False)
        oracle_corpus_bleu = bleu_tup[0]

        avg_sent_bleu = np.average(sent_bleu_scores)
        oracle_avg_sent_bleu = np.average(oracle_bleu_scores)
        exact = sum([1 if h == r else 0 for h, r in zip(hyp_code_tokens, tokenized_ref_snippets)]) / float(
            len(examples))
        oracle_exact_match = np.average(oracle_exact_match)

        return {'corpus_bleu': corpus_bleu,
                'oracle_corpus_bleu': oracle_corpus_bleu,
                'avg_sent_bleu': avg_sent_bleu,
                'oracle_avg_sent_bleu': oracle_avg_sent_bleu,
                'exact_match': exact,
                'oracle_exact_match': oracle_exact_match}

    def evaluate_dataset(self, dataset, decode_results, fast_mode=False, args=None):
        _, _, canonic_to_orig_name = load_docs()

        examples = dataset.examples if isinstance(dataset, Dataset) else dataset
        assert len(examples) == len(decode_results)

        def get_func_names(code_f):
            sketch = Parser(code_f).generate()
            f_names = [f['name'] for f in sketch.ast_visitor.functions]
            if '.' in f_names:
                print('wtf')
            return f_names

        def get_code_orig_names(code_f):
            code_orig_names = code_f
            f_names = get_func_names(code_f)
            for f_name in f_names:
                if f_name in canonic_to_orig_name:
                    orig_name = canonic_to_orig_name[f_name]
                    if not re.findall("dict\.|str\.|list\.", orig_name):
                        code_orig_names = code_orig_names.replace(f_name, orig_name)
            return code_orig_names

        # 0. Renamed functions eval

        for example in examples:
            setattr(example, 'reference_code_tokens',
                    get_func_names(example.meta['example_dict']['canonic']))

        for i, example in enumerate(examples):
            hyp_list = decode_results[i]
            # here we prune any hypothesis that throws an error when converting back to the decanonical code!
            # This modifies the decode_results in-place!
            filtered_hyp_list = []
            for hyp in hyp_list:
                try:
                    setattr(hyp, 'decanonical_code', decanonicalize_code(hyp.code, slot_map=example.meta['slot_map']))
                    setattr(hyp, 'decanonical_code_tokens', get_func_names(hyp.decanonical_code))
                    filtered_hyp_list.append(hyp)
                except: pass
            decode_results[i] = filtered_hyp_list

        output_plaintext_file_name = args.save_decode_to + '-just_funcs' if args.save_decode_to else None
        ret_just_functions_eval = self.evaluate_dataset_helper(examples, decode_results, output_plaintext_file_name)
        # del ret_just_functions_eval['exact_match']
        # del ret_just_functions_eval['oracle_exact_match']

        # 1. Renamed functions eval

        for example in examples:
            setattr(example, 'reference_code_tokens',
                    tokenize_for_bleu_eval(example.meta['example_dict']['canonic']))

        for i, example in enumerate(examples):
            hyp_list = decode_results[i]
            # here we prune any hypothesis that throws an error when converting back to the decanonical code!
            # This modifies the decode_results in-place!
            filtered_hyp_list = []
            for hyp in hyp_list:
                try:
                    setattr(hyp, 'decanonical_code', decanonicalize_code(hyp.code, slot_map=example.meta['slot_map']))
                    setattr(hyp, 'decanonical_code_tokens', tokenize_for_bleu_eval(hyp.decanonical_code))
                    filtered_hyp_list.append(hyp)
                except:
                    pass
            decode_results[i] = filtered_hyp_list

        output_plaintext_file_name = args.save_decode_to + '-renamed_funcs' if args.save_decode_to else None
        ret_functions_eval = self.evaluate_dataset_helper(examples, decode_results, output_plaintext_file_name)

        # 2. Original eval
        for example in examples:
            setattr(example, 'reference_code_tokens',
                    tokenize_for_bleu_eval(example.meta['example_dict']['snippet']))

        for i, example in enumerate(examples):
            hyp_list = decode_results[i]
            # here we prune any hypothesis that throws an error when converting back to the decanonical code!
            # This modifies the decode_results in-place!
            filtered_hyp_list = []
            for hyp in hyp_list:
                try:
                    setattr(hyp, 'code', get_code_orig_names(hyp.code))
                    setattr(hyp, 'decanonical_code',
                            decanonicalize_code(hyp.code, slot_map=example.meta['slot_map']))
                    setattr(hyp, 'decanonical_code_tokens', tokenize_for_bleu_eval(hyp.decanonical_code))
                    filtered_hyp_list.append(hyp)
                except:
                    pass

            decode_results[i] = filtered_hyp_list

        output_plaintext_file_name = args.save_decode_to + '-original' if args.save_decode_to else None
        ret = self.evaluate_dataset_helper(examples, decode_results, output_plaintext_file_name)
        # del ret['exact_match']
        # del ret['oracle_exact_match']

        for k, v in ret_functions_eval.items():
            ret['renamed_funcs_' + k] = v
        for k, v in ret_just_functions_eval.items():
            ret['just_funcs_' + k] = v

        return ret

    # def evaluate_dataset_old(self, dataset, decode_results, fast_mode=False, args=None, canonic_to_orig_name=None):
    #     output_plaintext_file = None
    #     if args and args.save_decode_to:
    #         output_plaintext_file = open(args.save_decode_to + '.txt', 'w', encoding='utf-8')
    #     examples = dataset.examples if isinstance(dataset, Dataset) else dataset
    #     assert len(examples) == len(decode_results)
    #
    #     def code_orig_names(code_f):
    #         code_orig_names = code_f
    #
    #         sketch = Parser(code_f).generate()
    #         f_names = [f['name'] for f in sketch.ast_visitor.functions]
    #         for f_name in f_names:
    #             code_orig_names.replace(f_name, canonic_to_orig_name[f_name])
    #         return code_orig_names

    #     # speed up, cache tokenization results
    #     if not hasattr(examples[0], 'reference_code_tokens'):
    #         for example in examples:
    #             setattr(example, 'reference_code_tokens', tokenize_for_bleu_eval(example.meta['example_dict']['snippet']))
    #
    #     if not hasattr(examples[0], 'reference_code_tokens_f'):
    #         for example in examples:
    #             setattr(example, 'reference_code_tokens_f', tokenize_for_bleu_eval(example.meta['example_dict']['canonic']))
    #
    #     for i, example in enumerate(examples):
    #         hyp_list = decode_results[i]
    #         # here we prune any hypothesis that throws an error when converting back to the decanonical code!
    #         # This modifies the decode_results in-place!
    #         filtered_hyp_list = []
    #         for hyp in hyp_list:
    #             setattr(hyp, 'decanonical_code_f', decanonicalize_code(hyp.code, slot_map=example.meta['slot_map']))
    #             setattr(hyp, 'decanonical_code_tokens_f', tokenize_for_bleu_eval(hyp.decanonical_code_f))
    #
    #             setattr(hyp, 'code_orig_names', code_orig_names(hyp.code))
    #             setattr(hyp, 'decanonical_code_orig', decanonicalize_code(hyp.code_orig_names, slot_map=example.meta['slot_map']))
    #             setattr(hyp, 'decanonical_code_tokens_orig', tokenize_for_bleu_eval(hyp.decanonical_code_orig))
    #
    #             filtered_hyp_list.append(hyp)
    #
    #         decode_results[i] = filtered_hyp_list
    #
    #     if fast_mode:
    #         # references = [e.reference_code_tokens for e in examples]
    #         # hypotheses = [hyp_list[0].decanonical_code_tokens if hyp_list else [] for hyp_list in decode_results]
    #         #
    #         # bleu_tup = compute_bleu([[x] for x in references], hypotheses, smooth=False)
    #         # bleu = bleu_tup[0]
    #         #
    #         # return bleu
    #         return None
    #     else:
    #         tokenized_ref_snippets = []
    #         tokenized_ref_snippets_f = []
    #         hyp_code_tokens = []
    #         best_hyp_code_tokens = []
    #         sm_func = SmoothingFunction().method3
    #         sent_bleu_scores = []
    #         oracle_bleu_scores = []
    #         oracle_exact_match = []
    #         for example, hyp_list in zip(examples, decode_results):
    #             tokenized_ref_snippets.append(example.reference_code_tokens)
    #             tokenized_ref_snippets_f.append(example.reference_code_tokens_f)
    #             example_hyp_bleu_scores = []
    #             example_hyp_bleu_scores_f = []
    #             if hyp_list:
    #                 for i, hyp in enumerate(hyp_list):
    #                     hyp.bleu_score = sentence_bleu([example.reference_code_tokens],
    #                                                    hyp.decanonical_code_tokens,
    #                                                    smoothing_function=sm_func)
    #                     hyp.bleu_score_f = sentence_bleu([example.reference_code_tokens_f],
    #                                                    hyp.decanonical_code_tokens,
    #                                                    smoothing_function=sm_func)
    #                     hyp.is_correct = self.is_hyp_correct(example, hyp)
    #
    #                     example_hyp_bleu_scores.append(hyp.bleu_score)
    #                     example_hyp_bleu_scores_f.append(hyp.bleu_score_f)
    #
    #                 top_decanonical_code_tokens = hyp_list[0].decanonical_code_tokens
    #                 sent_bleu_score = hyp_list[0].bleu_score
    #                 best_hyp_idx = np.argmax(example_hyp_bleu_scores)
    #                 oracle_sent_bleu = example_hyp_bleu_scores[best_hyp_idx]
    #                 _best_hyp_code_tokens = hyp_list[best_hyp_idx].decanonical_code_tokens
    #
    #                 best_hyp_idx_f = np.argmax(example_hyp_bleu_scores_f)
    #                 oracle_sent_bleu_f = example_hyp_bleu_scores_f[best_hyp_idx_f]
    #                 _best_hyp_code_tokens_f = hyp_list[best_hyp_idx_f].decanonical_code_tokens
    #             else:
    #                 top_decanonical_code_tokens = []
    #                 sent_bleu_score = 0.
    #                 oracle_sent_bleu = 0.
    #                 _best_hyp_code_tokens = []
    #
    #             # write results to file
    #             if output_plaintext_file:
    #                 output_plaintext_file.write(" ".join(top_decanonical_code_tokens) + '\n')
    #             oracle_exact_match.append(any(hyp.is_correct for hyp in hyp_list))
    #             hyp_code_tokens.append(top_decanonical_code_tokens)
    #             sent_bleu_scores.append(sent_bleu_score)
    #             oracle_bleu_scores.append(oracle_sent_bleu)
    #             best_hyp_code_tokens.append(_best_hyp_code_tokens)
    #
    #         bleu_tup = compute_bleu([[x] for x in tokenized_ref_snippets], hyp_code_tokens, smooth=False)
    #         corpus_bleu = bleu_tup[0]
    #
    #         bleu_tup = compute_bleu([[x] for x in tokenized_ref_snippets], best_hyp_code_tokens, smooth=False)
    #         oracle_corpus_bleu = bleu_tup[0]
    #
    #         avg_sent_bleu = np.average(sent_bleu_scores)
    #         oracle_avg_sent_bleu = np.average(oracle_bleu_scores)
    #         exact = sum([1 if h == r else 0 for h, r in zip(hyp_code_tokens, tokenized_ref_snippets)]) / float(
    #             len(examples))
    #         oracle_exact_match = np.average(oracle_exact_match)
    #
    #         return {'corpus_bleu': corpus_bleu,
    #                 'oracle_corpus_bleu': oracle_corpus_bleu,
    #                 'avg_sent_bleu': avg_sent_bleu,
    #                 'oracle_avg_sent_bleu': oracle_avg_sent_bleu,
    #                 'exact_match': exact,
    #                 'oracle_exact_match': oracle_exact_match}
