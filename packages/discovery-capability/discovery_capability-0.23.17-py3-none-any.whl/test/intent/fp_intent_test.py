import unittest
import os
from pathlib import Path
import shutil
from datetime import datetime
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from ds_core.properties.property_manager import PropertyManager
from sklearn.linear_model import LogisticRegression

from ds_capability import *
from ds_capability.components.commons import Commons

from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score

from ds_capability.intent.feature_predict_intent import FeaturePredictIntent

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class FeaturePredictIntentTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # clean out any old environments
        for key in os.environ.keys():
            if key.startswith('HADRON'):
                del os.environ[key]
        # Local Domain Contract
        os.environ['HADRON_PM_PATH'] = os.path.join('working', 'contracts')
        os.environ['HADRON_PM_TYPE'] = 'parquet'
        # Local Connectivity
        os.environ['HADRON_DEFAULT_PATH'] = Path('working/data').as_posix()
        # Specialist Component
        try:
            os.makedirs(os.environ['HADRON_PM_PATH'])
        except OSError:
            pass
        try:
            os.makedirs(os.environ['HADRON_DEFAULT_PATH'])
        except OSError:
            pass
        try:
            shutil.copytree('../_test_data', os.path.join(os.environ['PWD'], 'working/source'))
        except OSError:
            pass
        PropertyManager._remove_all()

    def tearDown(self):
        try:
            shutil.rmtree('working')
        except OSError:
            pass

    def test_for_smoke(self):
        # Model build
        X, y = load_iris(return_X_y=True)
        columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        params = {"solver": "lbfgs", "max_iter": 1000, "multi_class": "auto", "random_state": 8888}
        model = LogisticRegression(**params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        # model register
        fp = FeaturePredict.from_env('tester', has_contract=False)
        fp.add_connector_persist('RandomForestClassifier', 'model_test.parquet')
        fp.add_trained_model('RandomForestClassifier', model, metrics=("accuracy", accuracy), params=params)
        # test
        tbl = pa.Table.from_arrays(X_test.T, names=columns)
        predict = fp.tools.label_predict(tbl, model_name='RandomForestClassifier')
        print(predict)

    def test_raise(self):
        startTime = datetime.now()
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))
        print(f"Duration - {str(datetime.now() - startTime)}")


def tprint(t: pa.table, headers: [str, list] = None, d_type: [str, list] = None,
           regex: [str, list] = None):
    _ = Commons.filter_columns(t.slice(0, 10), headers=headers, d_types=d_type, regex=regex)
    print(Commons.table_report(_).to_string())


if __name__ == '__main__':
    unittest.main()
