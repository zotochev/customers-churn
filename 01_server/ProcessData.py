import os.path
import pickle
import json
from datetime import datetime

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier


class ProcessData():
    def __init__(self, model_pickle):
        self.no_changes_need_ = [
                            'VEHICLE_IN_CREDIT',
                            'CLIENT_HAS_DAGO',
                            'CLIENT_HAS_OSAGO',
                            'POLICY_HAS_COMPLAINTS',
                            ]
        self.dummies_ = {
                            'POLICY_CLM_GLT_N':     ['0', '1S', '2', '1L', '4+', '3', 'n/d'],
                            'POLICY_CLM_N':         ['0', '1S', '2', '1L', '3', '4+', 'n/d'],
                            'POLICY_PRV_CLM_GLT_N': ['N', '0', '1L', '1S', '2', '3', '4+'],
                            'POLICY_PRV_CLM_N':     ['N', '0', '1L', '1S', '2', '3', '4+']
                            }
        self.true_false_ = {
                            'POLICY_BRANCH': lambda x: int(x == 'Москва'),
                            'INSURER_GENDER': lambda x: int(x == 'M'),
                            'CLAIM_AVG_ACC_ST_PRD': lambda x: int(int(x) == 0),
                            'POLICY_DEDUCT_VALUE': lambda x: int(int(x) == 0),
                            }
        self.to_categories_ = {
                            'POLICY_MIN_AGE': [[18, 34], [35, 41], [42, 50], [51, float('inf')],],
                            'POLICY_MIN_DRIVING_EXPERIENCE': [[0, 8], [9, 14], [15, 19], [20, float('inf')],],
                            'VEHICLE_ENGINE_POWER': [[0, 117], [118, 140], [141, 146], [147, 150], [151, 180], [181, float('inf')],],
                            'VEHICLE_SUM_INSURED': [[0, 550_000], [550_001, 810_000], [810_001, 1_160_000], [1_160_001, float('inf')],],
                            'POLICY_YEARS_RENEWED_N':[[0, 0], [1, 1], [2, float('inf')]],
                            }
        self.df = None 
        self.model = model_pickle 
        #self.model = pickle.load(model_pickle.read())
        self.prediction = None 
        self.ids = None 
        self.y = None 
        self.X = None 

    def insert_json_data(self, json_data):
        # read from json
        # The way data frame should be prepared:
        # json_data = test.to_json(orient="split")
         
        parsed = json.loads(json_data)
        #parsed = json_data
        if set(parsed.keys()) != set(['index', 'columns', 'data']):
            print('insert_json_data: Json data has wrong keys')
            return None
        data = pd.DataFrame(
                parsed['data'],
                index=parsed['index'],
                columns=parsed['columns']
                )

        set_data_columns = set(data.columns)
        set_ncn = set(self.no_changes_need_)
        set_d = set(self.dummies_.keys())
        set_tf = set(self.true_false_.keys())
        set_c = set(self.to_categories_.keys())

        if set_data_columns.intersection(set_ncn) != set_ncn \
                or set_data_columns.intersection(set_d) != set_d \
                or set_data_columns.intersection(set_tf) != set_tf \
                or set_data_columns.intersection(set_c) != set_c \
                :
            print('insert_json_data: resulted DataFrame doesn\'t have required columns')
            return None
        # prepare data
        data['POLICY_YEARS_RENEWED_N'] = data['POLICY_YEARS_RENEWED_N'].replace('N', '0')
        data['POLICY_YEARS_RENEWED_N'] = data['POLICY_YEARS_RENEWED_N'].astype('int32')

        data['POLICY_MIN_DRIVING_EXPERIENCE'] = data['POLICY_MIN_DRIVING_EXPERIENCE'].apply(self.fix_driving_experience)

        # no changes need
        self.df = data[self.no_changes_need_].copy()

        # dummies
        for column, list_dummies in self.dummies_.items():
            for dummy in list_dummies:
                self.df['{}_{}'.format(column, dummy)] = data[column].apply(lambda x: int(x == dummy))

        # true_false
        for column, function in self.true_false_.items():
            self.df[column] = data[column].apply(function)

        # categories
        for column, categories in self.to_categories_.items():
            for category in categories:
                self.df['{}_{}_{}'.format(column, category[0], category[1])] = data[column].apply(lambda x: int(category[0] <= x and x <= category[1]))

        # possibly no need
        # self.y = self.df['POLICY_IS_RENEWED']
        self.X = self.df

        self.ids = data['POLICY_ID'].copy()
        # del data
        return self.df

    def predict(self):
        if self.model is not None \
                and self.df is not None \
                and self.X is not None\
                :
            self.prediction = pd.DataFrame({'POLICY_ID': self.ids, 'POLICY_IS_RENEWED': self.model.predict(self.X), 'POLICY_IS_RENEWED_PROBABILITY': 0})
            return self.prediction.to_json(orient="split")
        else:
            print("ProcessData: Error: model is not prepared for prediction")

    @staticmethod
    def fix_driving_experience(x):
        if x > 1000:
            return datetime.now().year - x
        else:
            return x


def main():
    a = ProcessData("model.pkl")
    with open("json_data") as jd:
        insert_json_rv = a.insert_json_data(jd.read())
    if insert_json_rv is not None:
        result = a.predict()
        with open('{}'.format('json_predictions'), 'w') as f:
            f.write(result)
    else:
        print('insert json returned None')


if __name__ == "__main__":
    main()
