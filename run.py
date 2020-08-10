import os
import sys
import exp


model_1_name = "t10-funcs10-renamed_fs-patience7-renamed_bleu_metric-last_cell-just_train_set"
# model_2_name = "model_2_t1-orig-train-renamed_fs"
bin_dir = 'conala_new'
PRETRAIN, TRAIN, TEST, PRETRAIN_FUNCS, TRAIN_FUNCS = '1', '2', 't', '6', '7'

MODE = TRAIN_FUNCS
model_2_name = "t15-funcs10-renamed_fs-patience7-renamed_bleu_metric-last_cell-just_train_set-NEW_DOCS-new_vocab"


class BaseArgs:
    # common for both pretrain & train
    seed = 1
    mined_num = 100000
    ret_method = "snippet_count100k_topk1_temp2"
    freq = 3

    # vocab = f"data/{bin_dir}/vocab.src_freq3.code_freq3.bin"
    vocab = f"data/conala_new/vocab.src_freq3.code_freq3.bin"

    # vocab = f"data/conala/vocab.src_freq{freq}.code_freq{freq}.mined_{mined_num}.goldmine_{ret_method}.bin"
    # vocab = f"data/{bin_dir}/vocab.src_freq3.code_freq3.mined_100000.bin"
    # dev_file = "data/conala/dev.bin"  # TODO

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
    # evaluator = 'conala_evaluator'  # TODO: original
    evaluator = 'conala_functions_evaluator'
    verbose = False
    patience = 7
    max_num_trial = 7
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
    glove_embed_path = 'data/conala_new/glove.6B.100d.txt'  # None
    word_dropout = 0.
    decoder_word_dropout = 0.3
    primitive_token_label_smoothing = 0.0
    src_token_label_smoothing = 0.0
    negative_sample_type = 'best'
    valid_metric = 'acc'
    valid_every_epoch = 1
    save_all_models = False
    save_all_models_every25 = False

    uniform_init = None
    clip_grad = 5.
    optimizer = 'Adam'
    decay_lr_every_epoch = False
    reset_optimizer = False
    eval_top_pred_only = False
    example_preprocessor = None
    decode_max_time_step = 100
    save_decode_to = None
    att_vec_size = 256
    no_func_copy = True  #consistency
    # use_bert_encodings = False


class PretrainFuncsArgs(BaseArgs):
    # def __init__(self, model_name=model_1_name):
    #     BaseArgs.__init__(self)
    #
    #     self.mode = 'train'
    #     self.train_file = f"data/{bin_dir}/mined_100000.bin"
    #     self.batch_size = 64
    #     self.pretrain = False
    #     self.save_to = f'saved_models/conala/{model_name}'
    #     self.dev_file = f"data/{bin_dir}/dev.bin"

    def __init__(self, model_name=model_1_name):
        BaseArgs.__init__(self)

        self.model_name = model_name
        self.no_func_copy = False
        self.mode = 'train'
        self.train_file = f"data/{bin_dir}/renamed_funcs_apidocs.bin"
        self.dev_file = f"data/{bin_dir}/dev.bin"

        self.batch_size = 64
        self.pretrain = None  # f"saved_models/conala/{model_1_name}.bin"  # TODO for finetuning
        self.save_to = f'saved_models/conala/{self.model_name}'


class FinetuneArgs(BaseArgs):
    def __init__(self, model_name=model_2_name):
        BaseArgs.__init__(self)

        self.model_name = model_name
        self.mode = 'train'
        self.train_file = f"data/{bin_dir}/train.all_100000.bin"
        self.dev_file = f"data/{bin_dir}/dev.bin"
        self.batch_size = 10
        self.pretrain = None  # f"saved_models/conala/{model_1_name}.bin"  # TODO for finetuning
        self.save_to = f'saved_models/conala/{self.model_name}'
        # self.use_bert_encodings = True


class TrainWithFuncs(BaseArgs):
    def __init__(self, model_name=model_2_name):
        BaseArgs.__init__(self)

        self.model_name = model_name
        self.no_func_copy = False
        self.mode = 'train'
        self.train_file = f"data/{bin_dir}/train.all_0.bin"
        self.dev_file = f"data/{bin_dir}/dev.bin"

        self.batch_size = 10
        self.pretrain = None  # f"saved_models/conala/{model_1_name}.bin"  # TODO for finetuning
        self.save_to = f'saved_models/conala/{self.model_name}'


class TestArgs(BaseArgs):
    def __init__(self, model_test_name):
        BaseArgs.__init__(self)

        self.mode = 'test'
        self.load_model = f'saved_models/conala/{model_test_name}.bin'
        self.save_decode_to = f'decodes/conala/{model_test_name}.test.decode'
        # self.test_file = "data/conala/test.bin"  # TODO
        # self.test_file = "data/conala/added_funcs_test.bin"
        self.test_file = f"data/{bin_dir}/test.bin"
        self.cuda = False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.argv += [MODE]
    assert MODE in [PRETRAIN, TRAIN, TEST, PRETRAIN_FUNCS, TRAIN_FUNCS]

    train_args = None

    if sys.argv[1] == PRETRAIN_FUNCS:
        train_args = PretrainFuncsArgs()
    elif sys.argv[1] == TRAIN:
        train_args = FinetuneArgs()
    # elif sys.argv[1] == TEST:
    #     exp.main(TestArgs(model_2_name))
    elif sys.argv[1] == TRAIN_FUNCS:
        train_args = TrainWithFuncs()
    else:
        print("Unknown argument")

    exp.main(train_args)
    test_args = TestArgs(train_args.model_name)
    exp.main(test_args)
