import pickle
from asdl.hypothesis import *
from asdl.lang.py3.py3_transition_system import python_ast_to_asdl_ast, asdl_ast_to_python_ast, Python3TransitionSystem
from asdl.transition_system import *


if __name__ == '__main__':

    data = pickle.load(open("data/conala_resplit/train.all_0.bin", 'rb'))

    actions_dict = {}
    for e in data:
        for a in e.tgt_actions:
            if isinstance(a.action, ApplyRuleAction):
                if a.action.production not in actions_dict:
                    actions_dict[a.action.production] = 1
                else:
                    actions_dict[a.action.production] += 1

    top_actions = sorted(actions_dict.items(), key=lambda item: item[1], reverse=True)

    print('done')
