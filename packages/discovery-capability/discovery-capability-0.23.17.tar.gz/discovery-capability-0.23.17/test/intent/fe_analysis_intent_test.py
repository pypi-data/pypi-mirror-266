import unittest
import os
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from ds_capability import FeatureEngineer, FeatureSelect
from ds_capability.components.commons import Commons
from ds_capability.intent.feature_engineer_intent import FeatureEngineerIntent
from ds_core.properties.property_manager import PropertyManager

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class SyntheticTest(unittest.TestCase):

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
        os.environ['HADRON_PM_TYPE'] = 'json'
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

    def test_jitter(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        g = np.random.default_rng(1257643)
        arr = pa.array([0,0,1,5,3,-1,0,5,3])
        result = tools._jitter(arr, 12, generator=g)
        self.assertEqual([4, 0, 7, 0, 1, 0, 2, 0, 5, 0, 3, 1], result.to_pylist())
        arr = pa.array([0., 0., 1.1, 5., 3, -1, 0, 5, 3])
        result = tools._jitter(arr, 5, generator=g)
        self.assertEqual([4.6, 4.1, 0.0, 3.7, 0.0], result.to_pylist())


    def test_for_smoke(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        tbl = tools.get_synthetic_data_types(100, extend=True)
        fe.add_connector_uri('sample', './working/source/data_type.parquet')
        fe.save_canonical('sample', tbl)
        self.assertEqual((100, 17), tbl.shape)
        result = tools.get_analysis(1000, 'sample')
        self.assertEqual((1000, 17), result.shape)

    def test_group_analysis_sample(self):
        fs = FeatureSelect.from_memory()
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        # preprocess
        tbl = fs.set_source_uri('/Users/doatridge/code/jupyter/telecom/sentiment/source/TroubleTicket-20221213-115607.csv').load_source_canonical()
        tbl = fs.tools.auto_clean_header(tbl, case='lower')
        tbl = fs.tools.auto_drop_noise(tbl)
        tbl = fs.tools.auto_drop_duplicates(tbl)
        tbl = fe.tools.correlate_on_pandas(tbl, header='issue_notes',
                                           code_str="str.decode('utf-8', errors='replace')",
                                           to_header='issue_notes', intent_order=-1)
        tbl = fe.tools.correlate_on_pandas(tbl, header='resolution',
                                           code_str="str.decode('utf-8', errors='replace')",
                                           to_header='resolution', intent_order=-1)
        tbl = fe.tools.model_reinstate_nulls(tbl)
        # Negative
        condition = []
        for w in ['complai', 'unable', 'not able', 'constantly', 'not receiv', "didn't receiv"]:
            condition.append((w, 'match_substring', 'or'))

        tbl = fe.tools.correlate_on_condition(tbl, header='issue_notes', condition=condition, value='negative',
                                              default='neutral', to_header='sentiment')
        # Positive
        condition = []
        for w in ['mistakenly', 'requesting']:
            condition.append((w, 'match_substring', 'or'))

        tbl = fe.tools.correlate_on_condition(tbl, header='issue_notes', condition=condition, value='positive',
                                              default='@sentiment', to_header='sentiment')
        # Negative
        condition = []
        for w in ['Escalated', 'escalated']:
            condition.append((w, 'match_substring', 'or'))

        tbl = fe.tools.correlate_on_condition(tbl, header='resolution', condition=condition, value='negative',
                                              default='@sentiment', to_header='sentiment')
        # Analysis
        size = 100
        tbl = fe.tools.get_analysis_group(size=size, other=tbl, group_by='sentiment')
        print(tbl.shape)

    def test_group_analysis(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        tbl = tools.get_synthetic_data_types(10)
        arr = pa.array(list('0000111222'))
        tbl = Commons.table_append(pa.table([arr], ['User']), tbl)
        fe.add_connector_uri('sample', './working/source/data_type.parquet')
        fe.save_canonical('sample', tbl)
        result = tools.get_analysis_group(15, 'sample', 'User', 'date')
        # print(Commons.table_report(result).to_string())
        self.assertEqual((15, 8), result.shape)
        self.assertCountEqual([4, 5, 6], pc.value_counts(result.column('User')).field(1).to_pylist())
        self.assertEqual(result.column('date')[0], pc.min(result.column('date')))
        self.assertEqual(result.column('date')[-1], pc.max(result.column('date')))

    def test_direct_other(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        tbl = tools.get_synthetic_data_types(10, extend=True)
        result = tools.get_analysis(100, tbl)
        self.assertEqual((100, 17), result.shape)

    def test_flattened_sample(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        fe.add_connector_uri('sample', './working/source/complex_flatten_records.parquet')
        tbl = fe.load_canonical('sample')
        self.assertEqual((4, 20), tbl.shape)
        result = tools.get_analysis(6, 'sample')
        self.assertEqual((6, 20), result.shape)

    def test_complex_nested(self):
        fe = FeatureEngineer.from_memory()
        tools: FeatureEngineerIntent = fe.tools
        document = [
            {"_id": "I35138",
             "contactMedium": [
                {"medium": {"number": "50070028", "type": "mobile"}, "preferred": True},
                {"medium": {"emailAddress": "mail@stc.com.kw", "type": "emailAddress"}, "preferred": True}],
             "gender": "M", "familyName": "Fouad", "givenName": "Fouad", "middleName": "Fouad"},
            {"_id": "I35145",
             "contactMedium": [
                {"medium": {"emailAddress": "panneer.rajadurai.c@solutions.com.kw", "type": "EmailAddress"}, "preferred": True},
                {"medium": {"number": "51658317", "type": "mobile"}, "preferred": True},
                {"medium": {"number": "51658317", "type": "whatsapp"}, "preferred": False},
                {"medium": {"number": "51658317", "type": "telegram"}, "preferred": False},
                {"medium": {"type": "telephone"}, "role": "AlternateNumber"}],
             "gender": "M", "familyName": "Jay", "givenName": "Bhuvana", "middleName": ""},
            {"_id": "I35146",
             "contactMedium": [
                {"medium": {"emailAddress": "bhuvana.stc21@gmail.com", "type": "EmailAddress"}, "preferred": True},
                {"medium": {"type": "mobile"}, "preferred": False},
                {"medium": {"type": "whatsapp"}, "preferred": False},
                {"medium": {"type": "telegram"}, "preferred": False}],
             "gender": "F", "familyName": "CORP", "givenName": "TECNOTREE", "middleName": "LTD"},
            {"_id": "I35181",
             "contactMedium": [],
             "gender": "M", "familyName": "test", "givenName": "test", "nationality": "", "middleName": ""}
        ]
        tbl = pa.Table.from_pylist(document)
        tbl = Commons.table_flatten(tbl)
        result = tools.get_analysis(10, tbl)


    def test_raise(self):
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))


if __name__ == '__main__':
    unittest.main()
