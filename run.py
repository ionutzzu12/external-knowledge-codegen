import os
import sys
import exp


model_1_name = "model_1_t1"  # f"retdistsmpl.dr{dropout}.lr{lr}.lr_de{lr_decay}.lr_da{lr_decay_after_epoch}.beam{beam_size}.vocab.src_freq{freq}.code_freq{freq}.mined_{mined_num}.goldmine_{ret_method}.pre_{mined_num}_goldmine_{ret_method}.seed{seed}"
model_2_name = "model_2_t1"

PRETRAIN, TRAIN, TEST = '1', '2', 't'

MODE = PRETRAIN


class BaseArgs:
    # common for both pretrain & train
    seed = 0
    mined_num = 100000
    ret_method = "snippet_count100k_topk1_temp2"
    freq = 3
    vocab = f"data/conala/vocab.src_freq{freq}.code_freq{freq}.mined_{mined_num}.goldmine_{ret_method}.bin"
    dev_file = "data/conala/dev.bin"
    dropout = 0.3
    hidden_size = 256
    embed_size = 128
    action_embed_size = 128
    field_embed_size = 64
    type_embed_size = 64
    lr = 0.001
    lr_decay = 0.5
    beam_size = 15
    max_epoch = 80
    lstm = 'lstm'  # lstm
    lr_decay_after_epoch = 15

    cuda = True
    lang = 'python'
    asdl_file = 'asdl/lang/py3/py3_asdl.simplified.txt'
    parser = 'default_parser'
    transition_system = 'python3'
    evaluator = 'conala_evaluator'
    verbose = False
    patience = 5
    max_num_trial = 5
    glorot_init = True
    log_every = 50

    # defaults
    no_parent_field_type_embed = no_parent_production_embed = True
    no_parent_field_embed = False
    no_query_vec_to_action_embed = False
    readout = 'identity'
    no_query_vec_to_action_map = False
    query_vec_to_action_diff_map = False
    sup_attention = False
    no_parent_state = False
    no_input_feed = False
    no_copy = False
    glove_embed_path = None
    word_dropout = 0.
    decoder_word_dropout = 0.3
    primitive_token_label_smoothing = 0.0
    src_token_label_smoothing = 0.0
    negative_sample_type = 'best'
    valid_metric = 'acc'
    valid_every_epoch = 1
    save_all_models = False
    uniform_init = None
    clip_grad = 5.
    optimizer = 'Adam'
    decay_lr_every_epoch = 0
    reset_optimizer = False
    eval_top_pred_only = False
    example_preprocessor = None
    decode_max_time_step = 100
    save_decode_to = None
    att_vec_size = 256


class PretrainArgs(BaseArgs):
    def __init__(self):
        BaseArgs.__init__(self)

        self.mode = 'train'
        self.train_file = f"data/conala/pre_{self.mined_num}_goldmine_{self.ret_method}.bin"
        self.batch_size = 48  # 64
        self.pretrain = False
        self.save_to = f'saved_models/conala/{model_1_name}'


class FinetuneArgs(BaseArgs):
    def __init__(self):
        BaseArgs.__init__(self)

        self.mode = 'train'
        self.train_file = "data/conala/train.gold.full.bin"
        self.batch_size = 10
        self.pretrain = f"saved_models/conala/{model_1_name}.bin"
        self.save_to = f'saved_models/conala/{model_2_name}'


class TestArgs(BaseArgs):
    def __init__(self):
        BaseArgs.__init__(self)

        self.mode = 'test'
        self.load_model = f'saved_models/conala/{model_2_name}.bin'
        self.save_decode_to = f'decodes/conala/{model_2_name}.test.decode'
        self.test_file = "data/conala/test.bin"
        self.cuda = False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.argv += [MODE]
    assert MODE in [PRETRAIN, TRAIN, TEST]

    if sys.argv[1] == PRETRAIN:
        exp.main(PretrainArgs())
    elif sys.argv[1] == TRAIN:
        exp.main(FinetuneArgs())
    else:
        exp.main(TestArgs())
