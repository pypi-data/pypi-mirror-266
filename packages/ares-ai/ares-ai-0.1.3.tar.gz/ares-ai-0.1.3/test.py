from ares.ares import ARES
import pandas as pd


# ues_idp_config = {
#     # Dataset for in-domain prompts
#     "in_domain_prompts_dataset": "/future/u/manihani/ARES/data/datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
    
#     # Dataset for unlabeled evaluation
#     "unlabeled_evaluation_set": "/future/u/manihani/ARES/data/datasets_v2/nq/nq_ratio_0.5.tsv", 

#     "context_relevance_system_prompt": """You are an expert dialogue agent. Your task is to analyze the provided document and determine whether 
#     it is relevant for responding to the dialogue. Consider the content of the document and its relation to the provided dialogue. 
#     Output your final verdict in the format: "[[Yes]]" if the document is relevant, and "[[No]]" if the document provided is not relevant. 
#     Strictly adhere to this response format without any additional explanation.
#     """,

#     "answer_relevance_system_prompt": """Given a question, a document, and an answer, analyze both the provided answer and document to determine if the answer is relevant to the question. 
#     Evaluate whether the answer addresses all aspects of the question and relies solely on correct information from the document for its response. 
#     Output your final verdict in the format: "[[Yes]]" if the answer is relevant to the given question, and "[[No]]" if the answer is not relevant. 
#     Maintain strict adherence to this response format without additional explanation. """,
    
#     "answer_faithfulness_system_prompt": """Given a question, a document, and an answer, assess whether the provided answer is faithful to the document's contents. 
#     The answer must neither introduce information beyond what is contained in the document nor contradict any document information. 
#     Output your verdict in the format: "[[Yes]]" if the answer is faithful to the document, and "[[No]]" if the answer is unfaithful. 
#     Ensure strict adherence to this response format without providing additional details.
#     """,

#     "model_choice" : "meta-llama/Llama-2-70b-chat-hf"
# }

# ues_idp_config = {
#     # Dataset for in-domain prompts
#     "in_domain_prompts_dataset": "/future/u/manihani/ARES/data/datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
    
#     # Dataset for unlabeled evaluation
#     "unlabeled_evaluation_set": "/future/u/manihani/ARES/data/datasets_v2/nq/nq_ratio_0.5.tsv", 
    
#     # Model: Mistral 7B
#     "model_choice" : "gpt-3.5-turbo-0125"
# }

# synth_config = { 
#     "document_filepaths": ["/future/u/manihani/ARES/data/datasets_v2/nq/nq_ratio_0.5.tsv"],
#     "few_shot_prompt_filename": "/future/u/manihani/ARES/data/datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
#     "synthetic_queries_filenames": ["data/output/synthetic_queries_1.tsv"],
#     "documents_sampled": 20
# }

# # HOTPOTQA
# synth_config = { 
#     "document_filepaths": ["/future/u/manihani/ARES/data/datasets_v2/hotpotqa/ratio_0.6_reformatted_full_articles_False_validation_with_negatives.tsv"],
#     "few_shot_prompt_filename": "/future/u/manihani/ARES/data/datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
#     "synthetic_queries_filenames": ["data/output/hotpotqa_synthetc_queries_1.tsv"],
#     "documents_sampled": 50
# }

# ppi_config = { 
#     "evaluation_datasets": ['datasets_v2/nq/ratio_0.525_reformatted_full_articles_False_validation_with_negatives.tsv'], 
#     "few_shot_examples_filepath": "datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
#     "checkpoints": ["/future/u/manihani/ARES/example_checkpoints/Context-Relevance-Label.pt", "/future/u/manihani/ARES/example_checkpoints/Answer-Relevance-Validation-1867825.pt"],
#     "labels": ["Context_Relevance_Label", "Answer_Relevance_Label"], 
#     "GPT_scoring": False, 
#     "gold_label_path": "datasets_v2/nq/ratio_0.525_reformatted_full_articles_False_validation_with_negatives.tsv", 
#     "swap_human_labels_for_gpt4_labels": False
# }

# WoW 
# synth_config = { 
#     "document_filepaths": ["/future/u/manihani/ARES/data/datasets_v2/wow/ratio_0.6_reformatted_full_articles_False_validation_with_negatives.tsv"],
#     "few_shot_prompt_filename": "/future/u/manihani/ARES/data/datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
#     "synthetic_queries_filenames": ["data/output/WoW_synthetic_queries_1.tsv"],
#     "documents_sampled": 10000
# }


# classifier_config = {
#     "classification_dataset": "output/synthetic_queries_1.tsv", 
#     "test_set_selection": "/future/u/manihani/ARES/datasets_v2/nq/ratio_0.6_reformatted_full_articles_False_validation_with_negatives.tsv", 
#     "label_column": "Answer_Relevance_Label", 
#     "num_epochs": 10, 
#     "patience_value": 3, 
#     "learning_rate": 5e-6
# }

# TEST 
classifier_config = {
    "classification_dataset": "data/output/synthetic_queries_1.tsv", 
    "validation_set": "/future/u/manihani/ARES/data/datasets_v2/nq/nq_ratio_0.6.tsv", 
    "label_column": "Answer_Relevance_Label", 
    "num_epochs": 10, 
    "patience_value": 3, 
    "learning_rate": 5e-6
}

# ppi_config = { 
#     "evaluation_datasets": ['/future/u/manihani/ARES/data/datasets_v2/nq/nq_ratio_0.6.tsv'], 
#     "few_shot_examples_filepath": "/future/u/manihani/ARES/data/datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
#     "checkpoints": ["/future/u/manihani/ARES/data/example_checkpoints/5e-06_1_True_Context_Relevance_Label_ratio_0.6_reformatted_full_articles_False_validation_with_negatives_428380.pt"],
#     "labels": ["Context_Relevance_Label"], 
#     "GPT_scoring": False, 
#     "gold_label_path": "/future/u/manihani/ARES/data/datasets_v2/nq/nq_ratio_0.525.tsv", 
#     "swap_human_labels_for_gpt4_labels": False
# }

# ppi_config = { 
#     "evaluation_datasets": ['datasets_v2/nq/ratio_0.525_reformatted_full_articles_False_validation_with_negatives.tsv'], 
#     "few_shot_examples_filepath": "datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
#     "checkpoints": ["/future/u/manihani/ARES/example_checkpoints/Context-Relevance-Label.pt", "/future/u/manihani/ARES/example_checkpoints/Answer-Relevance-Validation-1867825.pt"],
#     "labels": ["Context_Relevance_Label", "Answer_Relevance_Label"], 
#     "GPT_scoring": False, 
#     "gold_label_path": "datasets_v2/nq/ratio_0.525_reformatted_full_articles_False_validation_with_negatives.tsv", 
#     "swap_human_labels_for_gpt4_labels": False
# }

# ppi_config = { 
#     "evaluation_datasets": ['/future/u/manihani/ARES/datasets_v2/nq/ratio_0.5_reformatted_full_articles_False_validation_with_negatives.tsv'], 
#     "few_shot_examples_filepath": "/future/u/manihani/ARES/datasets/multirc_few_shot_prompt_for_synthetic_query_generation_v1.tsv",
#     "checkpoints": ["/future/u/manihani/ARES/checkpoints/microsoft-deberta-v3-large/output-synthetic_queries_1.tsv/5e-06_1_True_Context_Relevance_Label_ratio_0.6_reformatted_full_articles_False_validation_with_negatives_428380.pt"],
#     "labels": ["Context_Relevance_Label"], 
#     "GPT_scoring": False, 
#     "gold_label_path": "/future/u/manihani/ARES/datasets_v2/nq/ratio_0.5_reformatted_full_articles_False_validation_with_negatives.tsv", 
#     "swap_human_labels_for_gpt4_labels": False
# }

# ares = ARES(ues_idp=ues_idp_config)
# results = ares.ues_idp()
# print(results)

# ares = ARES(synthetic_query_generator=synth_config)
# results = ares.generate_synthetic_data()
# print(results)

ares = ARES(classifier_model=classifier_config)
results = ares.train_classifier()
print(results)

# ares = ARES(ppi=ppi_config)
# results = ares.evaluate_RAG()
# print(results)

# ares = ARES() 
# ares.KILT_dataset("fever")