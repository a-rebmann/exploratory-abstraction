from const import PCA_S


class Config:

    def __init__(self, in_path, out_path, log_name, att_names, rep_name, clust="agglomerative", sim_metric="cosine", noise_tau=0, multi_clustering=False, dim_red=PCA_S, comp=2, with_ranker=True):
        self.in_path = in_path
        self.out_path = out_path
        self.log_name = log_name
        self.att_names = att_names
        self.rep_name = rep_name
        self.clust = clust
        self.sim_metric = sim_metric
        self.noise_tau = noise_tau
        self.multi_clustering = multi_clustering
        self.dim_red = dim_red if dim_red else "None"
        self.comp = comp
        self.with_ranker = with_ranker


    def __repr__(self):
        return self.log_name + "_" + self.rep_name + "_" + self.clust + "_" + str(self.noise_tau) + "_" + str(self.multi_clustering) + "_" + self.dim_red + "_" + str(self.comp)
