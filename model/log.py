from sklearn import preprocessing
from const import DATE_PATTERNS, XES_CASE


class Log:

    def __init__(self, pd_log, pd_fv):
        self.pd_log = pd_log
        self.pd_fv = pd_fv
        self.numerical_atts = set()
        self.categorical_atts = set()
        self.other_atts = set()
        self.encoders = dict()
        self.init_log()

    def init_log(self):
        for column in self.pd_log:
            if column == XES_CASE:
                continue
            if len(self.pd_log[column].unique()) == len(self.pd_log):
                #print(column, "id an Event ID")
                continue
            #print(column, self.pd_log.dtypes[column])
            if len(self.pd_log[column].unique()) <= 1 or column == "High Level Transition":
                self.other_atts.add(column)
                print("ignore", column)
                continue
            if self.pd_log.dtypes[column] == 'datetime64' or 'datetime64' in str(self.pd_log.dtypes[column]) or \
                    self.pd_log[column].sample(n=50).dropna().apply(
                            lambda x: check_for_date(str(x))).all():
                continue
            if self.pd_log.dtypes[column] == "int64" or self.pd_log.dtypes[column] == "float64":
                self.numerical_atts.add(column)

            elif self.pd_log.dtypes[column] == "object":
                if len(self.pd_log[column].dropna().unique()) <= 2 and "false" in [str(x).lower() for x in self.pd_log[column].dropna().unique()] and "true" in [str(x).lower() for x in self.pd_log[column].dropna().unique()]:
                    self.pd_log[column] = self.pd_log[column].astype(str).str.lower()
                self.categorical_atts.add(column)
                le = preprocessing.LabelEncoder()
                #print(column, list(self.pd_log[column].unique()))
                le.fit(list(self.pd_log[column].unique()))
                self.encoders[column] = le


def check_for_date(att):
    for pattern in DATE_PATTERNS:
        if pattern.search(att):
            return True
    return False
