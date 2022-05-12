

class Config:

    def __init__(self, in_path, out_path, log_name, clust="agglomerative", sim_metric="cosine"):
        self.in_path = in_path
        self.out_path = out_path
        self.log_name = log_name
        self.clust = clust
        self.sim_metric = sim_metric
