import os
import pickle


def write_linkage_matrix(config, linkage_matrix):
    with open(os.path.join(config.out_path, config.log_name + 'linkage_matrix.pkl'), 'wb') as f:
        pickle.dump(linkage_matrix, f)
