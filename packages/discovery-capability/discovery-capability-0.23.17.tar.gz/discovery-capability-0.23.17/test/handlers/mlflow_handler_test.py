import unittest
import os
from pathlib import Path
import shutil
import ast
from datetime import datetime
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from ds_core.properties.property_manager import PropertyManager
from ds_capability import *
from ds_capability.components.commons import Commons
from ds_capability.handlers.mlflow_handlers import MlflowPersistHandler
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class TemplateTest(unittest.TestCase):

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
        fe = FeatureEngineer.from_memory()
        fe.add_connector_uri('mlflow', uri='mlflow://127.0.0.1:5000/', experiment_name='hadron_experiment_01', secure=False)

        if fe.pm.has_connector('mlflow'):
            handler = fe.pm.get_connector_handler('mlflow')
            print(handler.search_experiments())
        model, X_test, params, metrics = self.model_experiment()
        canonical = MlflowPersistHandler.canonical_create(model_name='mlflow', trained_model=model, metrics=metrics, params=params)
        fe.save_canonical('mlflow', canonical)


    @staticmethod
    def model_experiment():
        # experiment
        data = datasets.load_iris()
        X = data.data
        y = data.target
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        params = {
            "n_estimators": 100,
            "max_depth": 6,
            "min_samples_split": 10,
            "min_samples_leaf": 4,
            "bootstrap": True,
            "oob_score": False,
            "random_state": 31,
        }
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        # Calculate error metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        # Assemble the metrics we're going to write into a collection
        metrics = {"mae": mae, "mse": mse, "rmse": rmse, "r2": r2}
        return model, X_test, params, metrics
        


def tprint(t: pa.table, headers: [str, list] = None, d_type: [str, list] = None, regex: [str, list] = None):
    _ = Commons.filter_columns(t.slice(0, 10), headers=headers, d_types=d_type, regex=regex)
    print(Commons.table_report(_).to_string())


if __name__ == '__main__':
    unittest.main()
