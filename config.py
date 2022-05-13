

class Config:

    def __init__(self, in_path, out_path, log_name, att_names, rep_name, clust="agglomerative", sim_metric="cosine", noise_tau=0, multi_clustering=False):
        self.in_path = in_path
        self.out_path = out_path
        self.log_name = log_name
        self.att_names = att_names
        self.rep_name = rep_name
        self.clust = clust
        self.sim_metric = sim_metric
        self.noise_tau = noise_tau
        self.multi_clustering = multi_clustering
