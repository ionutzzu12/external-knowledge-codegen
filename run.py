import os

# pretrain script
seed = 0
mined_num = 100000
ret_method = "snippet_count100k_topk1_temp2"
freq = 3
vocab = f"data/conala/vocab.src_freq{freq}.code_freq{freq}.mined_{mined_num}.goldmine_{ret_method}.bin"
train_file = f"data/conala/pre_{mined_num}_goldmine_{ret_method}.bin"
dev_file = "data/conala/dev.bin"
dropout = 0.3
hidden_size = 256
embed_size = 128
action_embed_size = 128
field_embed_size = 64
type_embed_size = 64
lr = 0.001
lr_decay = 0.5
batch_size = 16  # 64  # todo
max_epoch = 80
beam_size = 15
lstm = 'lstm'  # lstm
lr_decay_after_epoch = 15
model_1_name = "model_1_t0"  # f"retdistsmpl.dr{dropout}.lr{lr}.lr_de{lr_decay}.lr_da{lr_decay_after_epoch}.beam{beam_size}.vocab.src_freq{freq}.code_freq{freq}.mined_{mined_num}.goldmine_{ret_method}.pre_{mined_num}_goldmine_{ret_method}.seed{seed}"
test_file = "data/conala/test.bin"

# finetune script
ret_method = "snippet_count100k_topk1_temp2"
pretrained_model_name = f"saved_models/conala/{model_1_name}.bin"
finetune_file = "data/conala/train.gold.full.bin"  # todo
model_2_name = "model_2"  # finetune.mined.retapi.distsmpl.dr{dropout}.lr{lr}.lr_de{lr_decay}.lr_da{lr_decay_after_epoch}.beam{beam_size}.seed{seed}.mined_{mined_num}.{ret_method}

# rerank script
#dev_decode_file=$1".dev.bin.decode"
#test_decode_file=$1".test.decode"
#num_workers=70


# step 1 - pre-training
command1 = f"""
python -u exp.py \
    --cuda \
    --seed {seed} \
    --mode train \
    --batch_size {batch_size} \
    --evaluator conala_evaluator \
    --asdl_file asdl/lang/py3/py3_asdl.simplified.txt \
    --transition_system python3 \
    --train_file {train_file} \
    --dev_file {dev_file} \
    --vocab {vocab} \
    --lstm {lstm} \
    --no_parent_field_type_embed \
    --no_parent_production_embed \
    --hidden_size {hidden_size} \
    --embed_size {embed_size} \
    --action_embed_size {action_embed_size} \
    --field_embed_size {field_embed_size} \
    --type_embed_size {type_embed_size} \
    --dropout {dropout} \
    --patience 5 \
    --max_num_trial 5 \
    --glorot_init \
    --lr {lr} \
    --lr_decay {lr_decay} \
    --lr_decay_after_epoch {lr_decay_after_epoch} \
    --max_epoch {max_epoch} \
    --beam_size {beam_size} \
    --log_every 50 \
    --save_to saved_models/conala/{model_1_name}
"""

# step 2 - fine-tuning
command2 = f"""
python -u exp.py \
    --cuda \
    --seed {seed} \
    --mode train \
    --batch_size 10 \
    --evaluator conala_evaluator \
    --asdl_file asdl/lang/py3/py3_asdl.simplified.txt \
    --transition_system python3 \
    --train_file {finetune_file} \
    --dev_file {dev_file} \
    --pretrain {pretrained_model_name} \
    --vocab {vocab} \
    --lstm {lstm} \
    --no_parent_field_type_embed \
    --no_parent_production_embed \
    --hidden_size {hidden_size} \
    --embed_size {embed_size} \
    --action_embed_size {action_embed_size} \
    --field_embed_size {field_embed_size} \
    --type_embed_size {type_embed_size} \
    --dropout {dropout} \
    --patience 5 \
    --max_num_trial 5 \
    --glorot_init \
    --lr {lr} \
    --lr_decay {lr_decay} \
    --lr_decay_after_epoch {lr_decay_after_epoch} \
    --max_epoch {max_epoch} \
    --beam_size {beam_size} \
    --log_every 50 \
    --save_to saved_models/conala/{model_2_name} 
"""

print(command1)
os.system(command1)

# testing
test_command = f"""
python exp.py \
    --mode test \
    --load_model saved_models/conala/{model_2_name}.bin \
    --beam_size 15 \
    --test_file {dev_file} \
    --evaluator conala_evaluator \
    --save_decode_to decodes/conala/{model_2_name}.test.decode \
    --decode_max_time_step 100
"""
#     --load_model best_pretrained_models/reranker.conala.vocab.src_freq3.code_freq3.mined_100000.intent_count100k_topk1_temp5.bin \
#     --load_model best_pretrained_models/finetune.mined.retapi.distsmpl.dr0.3.lr0.001.lr_de0.5.lr_da15.beam15.seed0.mined_100000.intent_count100k_topk1_temp5.bin \

# print(test_command)
# os.system(test_command)
