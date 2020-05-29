import pickle
from asdl.transition_system import ApplyRuleAction, GenTokenAction
from operator import itemgetter


if __name__ == "__main__":

    train_data = pickle.load(open("../data/conala/train.gold.full.bin", 'rb'))
    dev_data = pickle.load(open("../data/conala/dev.bin", 'rb'))
    test_data = pickle.load(open("../data/conala/test.bin", 'rb'))
    # mined_data = pickle.load(open("../data/conala/mined_100000.bin", 'rb'))

    all_data = train_data + dev_data + test_data
    total_call_actions = 0
    # att_preceded_by_call_actions = 0

    what_is_after_call = {}
    what_tokens = {}

    for data in all_data:
        actions = data.tgt_actions

        for index, a in enumerate(actions):
            if isinstance(a.action, ApplyRuleAction) and a.action.production.constructor.name == 'Call':
                total_call_actions += 1
                after_call = []

                index += 1

                while index < len(actions) and isinstance(actions[index].action, ApplyRuleAction):
                    rule = actions[index].action.production.constructor.name
                    index += 1
                    after_call.append(rule)

                key = str(after_call)
                if key in what_is_after_call:
                    what_is_after_call[key] += 1
                else:
                    what_is_after_call[key] = 1

                tokens = []

                while index < len(actions) and isinstance(actions[index].action, GenTokenAction):
                    tokens.append(actions[index].action.token)
                    index += 1

                if key in what_tokens:
                    what_tokens[key] += [tokens]
                else:
                    what_tokens[key] = [tokens]

                # if index + 1 < len(actions):
                #     b = actions[index+1]
                #     if isinstance(b.action, ApplyRuleAction) and b.action.production.constructor.name == 'Attribute':
                #         # att_preceded_by_call_actions += 1
                #         pass
                #     else:
                #         what = True
                #     if isinstance(b.action, ApplyRuleAction):
                #         key = b.action.production.constructor.name
                #         if key in what_is_after_call:
                #             x, y = what_is_after_call[key]
                #             what_is_after_call[key] = x + 1, y
                #         else:
                #             what_is_after_call[key] = (1, {})
                #         if index + 2 < len(actions):
                #             c = actions[index + 2]
                #             # if isinstance(c.action, ApplyRuleAction) and c.action.production.constructor.name == 'Attribute':
                #                 # att_preceded_by_call_actions += 1
                #                 # pass
                #             # else:
                #             #     what = True
                #             if isinstance(c.action, ApplyRuleAction):
                #                 key2 = c.action.production.constructor.name
                #                 if key2 in what_is_after_call[key][1]:
                #                     x, y = what_is_after_call[key]
                #                     y[key2] += 1
                #                     what_is_after_call[key] = x, y
                #                 else:
                #                     x, y = what_is_after_call[key]
                #                     what_is_after_call[key] = x, {key2: 1}
                #             else:
                #                 print('!!')
                # else:
                #     print("call is last!")

    print("total_call_actions:", total_call_actions)
    print("what_is_after_call:")
    for k, j in sorted(what_is_after_call.items(), key=itemgetter(1)):
        print(j, k, what_tokens[k])

    print('done')
