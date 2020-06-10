import six

if six.PY3:
    from datasets.conala.evaluator import ConalaEvaluator
    from datasets.conala.evaluator_with_functions import ConalaFunctionsEvaluator

