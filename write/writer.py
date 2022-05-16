import os
import pickle


def write_linkage_matrix(config, linkage_matrix):
    with open(os.path.join(config.out_path, config.log_name + 'linkage_matrix.pkl'), 'wb') as f:
        pickle.dump(linkage_matrix, f)


def write_result_to_disk(config, text_gen):
    with open(os.path.join(config.out_path, config.log_name + '_result.pkl'), 'wb') as f:
        pickle.dump(text_gen, f)