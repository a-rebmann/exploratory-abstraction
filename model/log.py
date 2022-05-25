from sklearn import preprocessing
from const import DATE_PATTERNS


class Log:

    def __init__(self, pd_log, pd_fv):
        self.pd_log = pd_log
        self.pd_fv = pd_fv
        self.numerical_atts = set()
        self.categorical_atts = set()
        self.encoders = dict()
        self.init_log()

    def init_log(self):
        for column in self.pd_log:
            if self.pd_log.dtypes[column] == 'datetime64' or 'datetime64' in str(self.pd_log.dtypes[column]) or self.pd_log.sample(n=50).dropna().apply(
                lambda x: check_for_date(str(x[column])), axis=1).all():
                continue
            if self.pd_log.dtypes[column] == "int64" or self.pd_log.dtypes[column] == "float64":
                self.numerical_atts.add(column)
                print(column, self.pd_log.dtypes[column])

            elif self.pd_log.dtypes[column] == "object":
                print(column, self.pd_log.dtypes[column])
                self.categorical_atts.add(column)
                le = preprocessing.LabelEncoder()
                le.fit(list(self.pd_log[column].unique()))
                self.encoders[column] = le


def check_for_date(att):
    for pattern in DATE_PATTERNS:
        if pattern.search(att):
            return True
    return False
