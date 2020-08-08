
import torch
from transformers import *

# Transformers has a unified API
# for 10 transformer architectures and 30 pretrained weights.
#          Model          | Tokenizer          | Pretrained weights shortcut
MODELS = [#(BertModel,       BertTokenizer,       'bert-base-uncased'),
          # (OpenAIGPTModel,  OpenAIGPTTokenizer,  'openai-gpt'),
          (GPT2Model,       GPT2Tokenizer,       'gpt2'),
          # (CTRLModel,       CTRLTokenizer,       'ctrl'),
          # (TransfoXLModel,  TransfoXLTokenizer,  'transfo-xl-wt103'),
          # (XLNetModel,      XLNetTokenizer,      'xlnet-base-cased'),
          # (XLMModel,        XLMTokenizer,        'xlm-mlm-enfr-1024'),
          # (DistilBertModel, DistilBertTokenizer, 'distilbert-base-cased'),
          # (RobertaModel,    RobertaTokenizer,    'roberta-base'),
          # (XLMRobertaModel, XLMRobertaTokenizer, 'xlm-roberta-base'),
         ]

# To use TensorFlow 2.0 versions of the models, simply prefix the class names with 'TF', e.g. `TFRobertaModel` is the TF 2.0 counterpart of the PyTorch model `RobertaModel`

# Let's encode some text in a sequence of hidden-states using each model:
for model_class, tokenizer_class, pretrained_weights in MODELS:
    # Load pretrained model/tokenizer
    tokenizer = tokenizer_class.from_pretrained(pretrained_weights)
    model = model_class.from_pretrained(pretrained_weights)

    # Encode text
    input_ids = torch.tensor([tokenizer.encode("format float str_0 to str_1 and set as title of matplotlib plot var_0", add_special_tokens=True)])  # Add special tokens takes care of adding [CLS], [SEP], <s>... tokens in the right way for each model.
    print(model_class, ':', input_ids.shape)

    with torch.no_grad():
        last_hidden_states = model(input_ids)[0]  # Models outputs are now tuples


# from simpletransformers.language_representation import RepresentationModel
#
# sentences = ["a b c d e d_"]
# model = RepresentationModel(
#     model_type="bert",
#     model_name="bert-base-uncased",
#     use_cuda=True
# )
# word_vectors = model.encode_sentences(sentences, combine_strategy=None)
# assert word_vectors.shape == (2, 5, 768)


# import logging
#
# import pandas as pd
# from simpletransformers.seq2seq import Seq2SeqModel, Seq2SeqArgs
#
#
# logging.basicConfig(level=logging.INFO)
# transformers_logger = logging.getLogger("transformers")
# transformers_logger.setLevel(logging.WARNING)
#
# train_data = [
#     [
#         "Perseus “Percy” Jackson is the main protagonist and the narrator of the Percy Jackson and the Olympians series.",
#         "Percy is the protagonist of Percy Jackson and the Olympians",
#     ],
#     [
#         "Annabeth Chase is one of the main protagonists in Percy Jackson and the Olympians.",
#         "Annabeth is a protagonist in Percy Jackson and the Olympians.",
#     ],
# ]
#
# train_df = pd.DataFrame(train_data, columns=["input_text", "target_text"])
#
# eval_data = [
#     [
#         "Grover Underwood is a satyr and the Lord of the Wild. He is the satyr who found the demigods Thalia Grace, Nico and Bianca di Angelo, Percy Jackson, Annabeth Chase, and Luke Castellan.",
#         "Grover is a satyr who found many important demigods.",
#     ],
#     [
#         "Thalia Grace is the daughter of Zeus, sister of Jason Grace. After several years as a pine tree on Half-Blood Hill, she got a new job leading the Hunters of Artemis.",
#         "Thalia is the daughter of Zeus and leader of the Hunters of Artemis.",
#     ],
# ]
#
# eval_df = pd.DataFrame(eval_data, columns=["input_text", "target_text"])
#
# # Configure the model
# model_args = Seq2SeqArgs()
# model_args.num_train_epochs = 1  # 200
# model_args.no_save = True
# model_args.evaluate_generated_text = True
# model_args.evaluate_during_training = True
# model_args.evaluate_during_training_verbose = True
#
# model = Seq2SeqModel(
#     "roberta",
#     "roberta-base",
#     "bert-base-cased",
#     args=model_args,
#     use_cuda=False
# )
#
# # Train the model
# model.train_model(train_df, eval_data=eval_df)
#
# # Evaluate the model
# result = model.eval_model(eval_df)
#
# # Use the model for prediction
# print(
#     model.predict(
#         [
#             "Tyson is a Cyclops, a son of Poseidon, and Percy Jackson’s half brother. He is the current general of the Cyclopes army."
#         ]
#     )
# )
#
# # Loading a saved model
# model_reloaded = Seq2SeqModel(
#     "roberta",
#     encoder_decoder_name="outputs",
#     args=model_args,
# )
#
# # Use the model for prediction
# print(
#     model_reloaded.predict(
#         [
#             "Tyson is a Cyclops, a son of Poseidon, and Percy Jackson’s half brother. He is the current general of the Cyclopes army."
#         ]
#     )
# )
