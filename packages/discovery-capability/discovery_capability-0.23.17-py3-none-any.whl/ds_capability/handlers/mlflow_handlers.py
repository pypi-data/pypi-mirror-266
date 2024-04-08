import pickle
from typing import Any

import pyarrow as pa
from ds_core.handlers.abstract_handlers import AbstractSourceHandler, AbstractPersistHandler
from ds_core.handlers.abstract_handlers import ConnectorContract, HandlerFactory


class MlflowSourceHandler(AbstractSourceHandler):
    """ A MLFlow source handler"""

    def __init__(self, connector_contract: ConnectorContract):
        """ initialise the Handler passing the source_contract dictionary """
        # required module import
        self.mlflow = HandlerFactory.get_module('mlflow')
        super().__init__(connector_contract)
        _kwargs = {**self.connector_contract.query, **self.connector_contract.kwargs}
        # connection
        secure = _kwargs.get('secure', True)
        schema = 'https' if secure else 'http'
        self.tracker = self.mlflow.set_tracking_uri(uri=f"{schema}://{connector_contract.netloc}/")
        # experiment name
        experiment = self.set_experiment(experiment_name=_kwargs.get('experiment_name'),
                                         experiment_id=_kwargs.get('experiment_id'))
        self.experiment_id = experiment.experiment_id
        self.model_info = None
        self.run = None
        self._changed_flag = True

    def search_experiments(self, view_type: int=None, max_results: int=None, filter_string: str=None,
                           order_by:list=None) -> list:
        """"""
        view_type = view_type if isinstance(view_type, int) else 1
        return self.mlflow.search_experiments(view_type, max_results, filter_string, order_by)

    def set_experiment(self, experiment_name: str=None, experiment_id: str=None):
        """"""
        if self.mlflow.is_tracking_uri_set():
            if isinstance(experiment_name, str):
                return self.mlflow.set_experiment(experiment_name=experiment_name)
            if isinstance(experiment_id, str):
                return self.mlflow.set_experiment(experiment_id=experiment_id)
            return self.mlflow.set_experiment(experiment_name='hadron_default')
        raise ConnectionError("The MLFlow tracking uri is not set")

    def supported_types(self) -> list:
        return ['mlflow']

    def exists(self) -> bool:
        if self.model_info:
            return True
        return False

    def has_changed(self) -> bool:
        return self._changed_flag

    def reset_changed(self, changed: bool=None):
        """ manual reset to say the file has been seen. This is automatically called if the file is loaded"""
        changed = changed if isinstance(changed, bool) else False
        self._changed_flag = changed

    def load_canonical(self, **kwargs) -> pa.Table:
        if self.model_info:
            model = self.mlflow.sklearn.load_model(self.model_info.model_uri)
            self.reset_changed(False)
            byte_model = pa.array([pickle.dumps(model)], type=pa.binary())
            return pa.table(data=[byte_model], names=['model'])
        raise ReferenceError("No Model saved for the current experiment")

    def latest_model(self):
        if self.mlflow.is_tracking_uri_set():
            return self.mlflow.sklearn.load_model(self.model_info.model_uri)
        return None

    def latest_run(self):
        if self.run:
            data = self.run.data
            return data.params, data.metrics
        return None

    def infer_signature(self, data: pa.Table, target: pa.Array):
        return self.mlflow.models.infer_signature(data.to_pandas(), target.to_pandas())

    @staticmethod
    def canonical_create(model_name: str, trained_model: Any, metrics: dict=None, description: str=None,
                         params: dict=None) -> pa.Table:
        """"""
        descr = description if isinstance(description, str) else ""
        params = params if isinstance(params, dict) else {}
        metrics = metrics if isinstance(metrics, tuple) else {}
        byte_model = pa.array([pickle.dumps(trained_model)], type=pa.binary())
        byte_params = pa.array([pickle.dumps(params)], type=pa.binary())
        byte_metrics = pa.array([pickle.dumps(metrics)], type=pa.binary())
        return pa.table(data=[pa.array([model_name]), byte_model, pa.array([descr]), byte_params, byte_metrics],
                        names=['model_name', 'model', 'description', 'params', 'metrics'])

    @staticmethod
    def canonical_explode(canonical: pa.Table):
        """"""
        name = canonical.column('model_name')[0].as_py()
        description = canonical.column('description')[0].as_py()
        model = pickle.loads(canonical.column('model')[0].as_py())
        params = pickle.loads(canonical.column('params')[0].as_py())
        metrics = pickle.loads(canonical.column('metrics')[0].as_py())
        return name, model, description, params, metrics


class MlflowPersistHandler(MlflowSourceHandler, AbstractPersistHandler):

    def persist_canonical(self, canonical: pa.Table, signature: Any=None, **kwargs) -> bool:
        """ persists the canonical dataset """
        if not isinstance(self.connector_contract, ConnectorContract):
            return False
        name, model, description, params, metrics = self.canonical_explode(canonical)
        with self.mlflow.start_run() as run:
            self.mlflow.log_metrics(metrics)
            self.mlflow.log_params(params)
            model_info = self.mlflow.sklearn.log_model(sk_model=model, artifact_path=name, signature=signature)
        self.model_info = model_info
        self.run = run
        self.reset_changed(True)
        return True

    def remove_canonical(self, **kwargs) -> bool:
        if self.run:
            self.mlflow.delete_run(self.run.info.run_id)
        self.model_info = None
        self.run = None


    def backup_canonical(self, canonical: pa.Table, uri: str, **kwargs) -> bool:
        pass

