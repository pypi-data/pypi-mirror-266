#
# This code is auto-generated using the sklearn_wrapper_template.py_template template.
# Do not modify the auto-generated code(except automatic reformatting by precommit hooks).
#
import inspect
import os
import posixpath
from typing import Iterable, Optional, Union, List, Any, Dict, Callable, Set
from typing_extensions import TypeGuard
from uuid import uuid4

import cloudpickle as cp
import pandas as pd
import numpy as np
from numpy import typing as npt


import numpy
import sklearn
import sklearn.neural_network
from sklearn.utils.metaestimators import available_if

from snowflake.ml.modeling.framework.base import BaseTransformer, _process_cols
from snowflake.ml._internal import telemetry
from snowflake.ml._internal.exceptions import error_codes, exceptions, modeling_error_messages
from snowflake.ml._internal.env_utils import SNOWML_SPROC_ENV
from snowflake.ml._internal.utils import pkg_version_utils, identifier
from snowflake.snowpark import DataFrame, Session
from snowflake.snowpark._internal.type_utils import convert_sp_to_sf_type
from snowflake.ml.modeling._internal.model_trainer_builder import ModelTrainerBuilder
from snowflake.ml.modeling._internal.transformer_protocols import (
    ModelTransformHandlers,
    BatchInferenceKwargsTypedDict,
    ScoreKwargsTypedDict
)

from snowflake.ml.modeling._internal.model_transformer_builder import ModelTransformerBuilder

from snowflake.ml.modeling._internal.estimator_utils import (
    gather_dependencies,
    original_estimator_has_callable,
    transform_snowml_obj_to_sklearn_obj,
    validate_sklearn_args,
)

from snowflake.ml.model.model_signature import (
    DataType,
    FeatureSpec,
    ModelSignature,
    _infer_signature,
    _rename_signature_with_snowflake_identifiers,
    BaseFeatureSpec,
)
from snowflake.ml.model._signatures import utils as model_signature_utils

_PROJECT = "ModelDevelopment"
# Derive subproject from module name by removing "sklearn"
# and converting module name from underscore to CamelCase
# e.g. sklearn.linear_model -> LinearModel.
_SUBPROJECT = "".join([s.capitalize() for s in "sklearn.neural_network".replace("sklearn.", "").split("_")])

DATAFRAME_TYPE = Union[DataFrame, pd.DataFrame]

def _is_fit_transform_method_enabled() -> Callable[[Any], bool]:	
    def check(self: BaseTransformer) -> TypeGuard[Callable[..., object]]:	
        return False and callable(getattr(self._sklearn_object, "fit_transform", None))	
    return check	


class MLPClassifier(BaseTransformer):
    r"""Multi-layer Perceptron classifier
    For more details on this class, see [sklearn.neural_network.MLPClassifier]
    (https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html)

    Parameters
    ----------

    input_cols: Optional[Union[str, List[str]]]
        A string or list of strings representing column names that contain features.
        If this parameter is not specified, all columns in the input DataFrame except
        the columns specified by label_cols, sample_weight_col, and passthrough_cols
        parameters are considered input columns. Input columns can also be set after
        initialization with the `set_input_cols` method.
    
    label_cols: Optional[Union[str, List[str]]]
        A string or list of strings representing column names that contain labels.
        Label columns must be specified with this parameter during initialization
        or with the `set_label_cols` method before fitting.

    output_cols: Optional[Union[str, List[str]]]
        A string or list of strings representing column names that will store the
        output of predict and transform operations. The length of output_cols must
        match the expected number of output columns from the specific predictor or
        transformer class used.
        If you omit this parameter, output column names are derived by adding an
        OUTPUT_ prefix to the label column names for supervised estimators, or
        OUTPUT_<IDX>for unsupervised estimators. These inferred output column names
        work for predictors, but output_cols must be set explicitly for transformers.
        In general, explicitly specifying output column names is clearer, especially
        if you don’t specify the input column names.
        To transform in place, pass the same names for input_cols and output_cols.
        be set explicitly for transformers. Output columns can also be set after
        initialization with the `set_output_cols` method.

    sample_weight_col: Optional[str]
        A string representing the column name containing the sample weights.
        This argument is only required when working with weighted datasets. Sample
        weight column can also be set after initialization with the
        `set_sample_weight_col` method.

    passthrough_cols: Optional[Union[str, List[str]]]
        A string or a list of strings indicating column names to be excluded from any
        operations (such as train, transform, or inference). These specified column(s)
        will remain untouched throughout the process. This option is helpful in scenarios
        requiring automatic input_cols inference, but need to avoid using specific
        columns, like index columns, during training or inference. Passthrough columns
        can also be set after initialization with the `set_passthrough_cols` method.

    drop_input_cols: Optional[bool], default=False
        If set, the response of predict(), transform() methods will not contain input columns.

    hidden_layer_sizes: array-like of shape(n_layers - 2,), default=(100,)
        The ith element represents the number of neurons in the ith
        hidden layer.

    activation: {'identity', 'logistic', 'tanh', 'relu'}, default='relu'
        Activation function for the hidden layer.

        - 'identity', no-op activation, useful to implement linear bottleneck,
          returns f(x) = x

        - 'logistic', the logistic sigmoid function,
          returns f(x) = 1 / (1 + exp(-x)).

        - 'tanh', the hyperbolic tan function,
          returns f(x) = tanh(x).

        - 'relu', the rectified linear unit function,
          returns f(x) = max(0, x)

    solver: {'lbfgs', 'sgd', 'adam'}, default='adam'
        The solver for weight optimization.

        - 'lbfgs' is an optimizer in the family of quasi-Newton methods.

        - 'sgd' refers to stochastic gradient descent.

        - 'adam' refers to a stochastic gradient-based optimizer proposed
          by Kingma, Diederik, and Jimmy Ba

        Note: The default solver 'adam' works pretty well on relatively
        large datasets (with thousands of training samples or more) in terms of
        both training time and validation score.
        For small datasets, however, 'lbfgs' can converge faster and perform
        better.

    alpha: float, default=0.0001
        Strength of the L2 regularization term. The L2 regularization term
        is divided by the sample size when added to the loss.

    batch_size: int, default='auto'
        Size of minibatches for stochastic optimizers.
        If the solver is 'lbfgs', the classifier will not use minibatch.
        When set to "auto", `batch_size=min(200, n_samples)`.

    learning_rate: {'constant', 'invscaling', 'adaptive'}, default='constant'
        Learning rate schedule for weight updates.

        - 'constant' is a constant learning rate given by
          'learning_rate_init'.

        - 'invscaling' gradually decreases the learning rate at each
          time step 't' using an inverse scaling exponent of 'power_t'.
          effective_learning_rate = learning_rate_init / pow(t, power_t)

        - 'adaptive' keeps the learning rate constant to
          'learning_rate_init' as long as training loss keeps decreasing.
          Each time two consecutive epochs fail to decrease training loss by at
          least tol, or fail to increase validation score by at least tol if
          'early_stopping' is on, the current learning rate is divided by 5.

        Only used when ``solver='sgd'``.

    learning_rate_init: float, default=0.001
        The initial learning rate used. It controls the step-size
        in updating the weights. Only used when solver='sgd' or 'adam'.

    power_t: float, default=0.5
        The exponent for inverse scaling learning rate.
        It is used in updating effective learning rate when the learning_rate
        is set to 'invscaling'. Only used when solver='sgd'.

    max_iter: int, default=200
        Maximum number of iterations. The solver iterates until convergence
        (determined by 'tol') or this number of iterations. For stochastic
        solvers ('sgd', 'adam'), note that this determines the number of epochs
        (how many times each data point will be used), not the number of
        gradient steps.

    shuffle: bool, default=True
        Whether to shuffle samples in each iteration. Only used when
        solver='sgd' or 'adam'.

    random_state: int, RandomState instance, default=None
        Determines random number generation for weights and bias
        initialization, train-test split if early stopping is used, and batch
        sampling when solver='sgd' or 'adam'.
        Pass an int for reproducible results across multiple function calls.
        See :term:`Glossary <random_state>`.

    tol: float, default=1e-4
        Tolerance for the optimization. When the loss or score is not improving
        by at least ``tol`` for ``n_iter_no_change`` consecutive iterations,
        unless ``learning_rate`` is set to 'adaptive', convergence is
        considered to be reached and training stops.

    verbose: bool, default=False
        Whether to print progress messages to stdout.

    warm_start: bool, default=False
        When set to True, reuse the solution of the previous
        call to fit as initialization, otherwise, just erase the
        previous solution. See :term:`the Glossary <warm_start>`.

    momentum: float, default=0.9
        Momentum for gradient descent update. Should be between 0 and 1. Only
        used when solver='sgd'.

    nesterovs_momentum: bool, default=True
        Whether to use Nesterov's momentum. Only used when solver='sgd' and
        momentum > 0.

    early_stopping: bool, default=False
        Whether to use early stopping to terminate training when validation
        score is not improving. If set to true, it will automatically set
        aside 10% of training data as validation and terminate training when
        validation score is not improving by at least tol for
        ``n_iter_no_change`` consecutive epochs. The split is stratified,
        except in a multilabel setting.
        If early stopping is False, then the training stops when the training
        loss does not improve by more than tol for n_iter_no_change consecutive
        passes over the training set.
        Only effective when solver='sgd' or 'adam'.

    validation_fraction: float, default=0.1
        The proportion of training data to set aside as validation set for
        early stopping. Must be between 0 and 1.
        Only used if early_stopping is True.

    beta_1: float, default=0.9
        Exponential decay rate for estimates of first moment vector in adam,
        should be in [0, 1). Only used when solver='adam'.

    beta_2: float, default=0.999
        Exponential decay rate for estimates of second moment vector in adam,
        should be in [0, 1). Only used when solver='adam'.

    epsilon: float, default=1e-8
        Value for numerical stability in adam. Only used when solver='adam'.

    n_iter_no_change: int, default=10
        Maximum number of epochs to not meet ``tol`` improvement.
        Only effective when solver='sgd' or 'adam'.

    max_fun: int, default=15000
        Only used when solver='lbfgs'. Maximum number of loss function calls.
        The solver iterates until convergence (determined by 'tol'), number
        of iterations reaches max_iter, or this number of loss function calls.
        Note that number of loss function calls will be greater than or equal
        to the number of iterations for the `MLPClassifier`.
    """

    def __init__(  # type: ignore[no-untyped-def]
        self,
        *,
        hidden_layer_sizes=(100,),
        activation="relu",
        solver="adam",
        alpha=0.0001,
        batch_size="auto",
        learning_rate="constant",
        learning_rate_init=0.001,
        power_t=0.5,
        max_iter=200,
        shuffle=True,
        random_state=None,
        tol=0.0001,
        verbose=False,
        warm_start=False,
        momentum=0.9,
        nesterovs_momentum=True,
        early_stopping=False,
        validation_fraction=0.1,
        beta_1=0.9,
        beta_2=0.999,
        epsilon=1e-08,
        n_iter_no_change=10,
        max_fun=15000,
        input_cols: Optional[Union[str, Iterable[str]]] = None,
        output_cols: Optional[Union[str, Iterable[str]]] = None,
        label_cols: Optional[Union[str, Iterable[str]]] = None,
        passthrough_cols: Optional[Union[str, Iterable[str]]] = None,
        drop_input_cols: Optional[bool] = False,
        sample_weight_col: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.set_input_cols(input_cols)
        self.set_output_cols(output_cols)
        self.set_label_cols(label_cols)
        self.set_passthrough_cols(passthrough_cols)
        self.set_drop_input_cols(drop_input_cols)
        self.set_sample_weight_col(sample_weight_col)
        self._use_external_memory_version = False
        self._batch_size = -1        
        deps: Set[str] = set([f'numpy=={np.__version__}', f'scikit-learn=={sklearn.__version__}', f'cloudpickle=={cp.__version__}'])
        
        self._deps = list(deps)
        
        init_args = {'hidden_layer_sizes':(hidden_layer_sizes, (100,), False),
            'activation':(activation, "relu", False),
            'solver':(solver, "adam", False),
            'alpha':(alpha, 0.0001, False),
            'batch_size':(batch_size, "auto", False),
            'learning_rate':(learning_rate, "constant", False),
            'learning_rate_init':(learning_rate_init, 0.001, False),
            'power_t':(power_t, 0.5, False),
            'max_iter':(max_iter, 200, False),
            'shuffle':(shuffle, True, False),
            'random_state':(random_state, None, False),
            'tol':(tol, 0.0001, False),
            'verbose':(verbose, False, False),
            'warm_start':(warm_start, False, False),
            'momentum':(momentum, 0.9, False),
            'nesterovs_momentum':(nesterovs_momentum, True, False),
            'early_stopping':(early_stopping, False, False),
            'validation_fraction':(validation_fraction, 0.1, False),
            'beta_1':(beta_1, 0.9, False),
            'beta_2':(beta_2, 0.999, False),
            'epsilon':(epsilon, 1e-08, False),
            'n_iter_no_change':(n_iter_no_change, 10, False),
            'max_fun':(max_fun, 15000, False),}
        cleaned_up_init_args = validate_sklearn_args(
            args=init_args,
            klass=sklearn.neural_network.MLPClassifier
        )
        self._sklearn_object: Any = sklearn.neural_network.MLPClassifier(
            **cleaned_up_init_args,
        )
        self._model_signature_dict: Optional[Dict[str, ModelSignature]] = None
        # If user used snowpark dataframe during fit, here it stores the snowpark input_cols, otherwise the processed input_cols
        self._snowpark_cols: Optional[List[str]] = self.input_cols
        self._autogenerated = True
        self._class_name=MLPClassifier.__class__.__name__
        self._subproject = _SUBPROJECT


    def _get_rand_id(self) -> str:
        """
        Generate random id to be used in sproc and stage names.

        Returns:
            Random id string usable in sproc, table, and stage names.
        """
        return str(uuid4()).replace("-", "_").upper()

    def set_input_cols(self, input_cols: Optional[Union[str, Iterable[str]]]) -> "MLPClassifier":
        """
        Input columns setter.

        Args:
            input_cols: A single input column or multiple input columns.

        Returns:
            self
        """
        self.input_cols = _process_cols(input_cols)
        self._snowpark_cols = self.input_cols
        return self

    def _get_active_columns(self) -> List[str]:
        """"Get the list of columns that are relevant to the transformer."""
        selected_cols = (
            self.input_cols +
            self.label_cols +
            ([self.sample_weight_col] if self.sample_weight_col is not None else [])
        )
        return selected_cols

    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def fit(self, dataset: Union[DataFrame, pd.DataFrame]) -> "MLPClassifier":
        """Fit the model to data matrix X and target(s) y
        For more details on this function, see [sklearn.neural_network.MLPClassifier.fit]
        (https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier.fit)


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.

        Returns:
            self
        """
        self._infer_input_output_cols(dataset)
        if isinstance(dataset, DataFrame):
            session = dataset._session
            assert session is not None  # keep mypy happy
            # Specify input columns so column pruning will be enforced
            selected_cols = self._get_active_columns()
            if len(selected_cols) > 0:
                dataset = dataset.select(selected_cols)

            self._snowpark_cols = dataset.select(self.input_cols).columns

             # If we are already in a stored procedure, no need to kick off another one.
            if SNOWML_SPROC_ENV in os.environ:
                statement_params = telemetry.get_function_usage_statement_params(
                    project=_PROJECT,
                    subproject=_SUBPROJECT,
                    function_name=telemetry.get_statement_params_full_func_name(inspect.currentframe(), MLPClassifier.__class__.__name__),
                    api_calls=[Session.call],
                    custom_tags=dict([("autogen", True)]) if self._autogenerated else None,
                )
                pd_df: pd.DataFrame = dataset.to_pandas(statement_params=statement_params)
                pd_df.columns = dataset.columns
                dataset = pd_df

        model_trainer = ModelTrainerBuilder.build(
            estimator=self._sklearn_object,
            dataset=dataset,
            input_cols=self.input_cols,
            label_cols=self.label_cols,
            sample_weight_col=self.sample_weight_col,
            autogenerated=self._autogenerated,
            subproject=_SUBPROJECT,
            use_external_memory_version=self._use_external_memory_version,
            batch_size=self._batch_size,
        )
        self._sklearn_object = model_trainer.train()
        self._is_fitted = True
        self._get_model_signatures(dataset)
        return self

    def _batch_inference_validate_snowpark(
        self,
        dataset: DataFrame,
        inference_method: str,
    ) -> List[str]:
        """Util method to run validate that batch inference can be run on a snowpark dataframe and
        return the available package that exists in the snowflake anaconda channel

        Args:
            dataset: snowpark dataframe
            inference_method: the inference method such as predict, score...

        Raises:
            SnowflakeMLException: If the estimator is not fitted, raise error
            SnowflakeMLException: If the session is None, raise error

        Returns:
            A list of available package that exists in the snowflake anaconda channel
        """
        if not self._is_fitted:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.METHOD_NOT_ALLOWED,
                original_exception=RuntimeError(
                    f"Estimator {self.__class__.__name__} not fitted before calling {inference_method} method."
                ),
            )

        session = dataset._session
        if session is None:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.NOT_FOUND,
                original_exception=ValueError(
                    "Session must not specified for snowpark dataset."
                ),
            )
        # Validate that key package version in user workspace are supported in snowflake conda channel
        return pkg_version_utils.get_valid_pkg_versions_supported_in_snowflake_conda_channel(
            pkg_versions=self._get_dependencies(), session=session, subproject=_SUBPROJECT)

    @available_if(original_estimator_has_callable("predict"))  # type: ignore[misc]
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def predict(self, dataset: Union[DataFrame, pd.DataFrame]) -> Union[DataFrame, pd.DataFrame]:
        """Predict using the multi-layer perceptron classifier
        For more details on this function, see [sklearn.neural_network.MLPClassifier.predict]
        (https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier.predict)


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.

        Returns:
            Transformed dataset.
        """
        super()._check_dataset_type(dataset)
        inference_method = "predict"

        # This dictionary contains optional kwargs for batch inference. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: BatchInferenceKwargsTypedDict = dict()   
                                
        if isinstance(dataset, DataFrame):
            expected_type_inferred = ""
            # when it is classifier, infer the datatype from label columns
            if expected_type_inferred == "" and 'predict' in self.model_signatures:
                # Batch inference takes a single expected output column type. Use the first columns type for now.
                label_cols_signatures = [row for row in self.model_signatures['predict'].outputs if row.name in self.output_cols]
                if len(label_cols_signatures) == 0:
                    error_str = f"Output columns {self.output_cols} do not match model signatures {self.model_signatures['predict'].outputs}."
                    raise exceptions.SnowflakeMLException(
                        error_code=error_codes.INVALID_ATTRIBUTE,
                        original_exception=ValueError(error_str),
                    )

                expected_type_inferred = convert_sp_to_sf_type(
                    label_cols_signatures[0].as_snowpark_type()
                )
            
            self._deps = self._batch_inference_validate_snowpark(dataset=dataset, inference_method=inference_method)
            assert isinstance(dataset._session, Session) # mypy does not recognize the check in _batch_inference_validate_snowpark()

            transform_kwargs = dict(
                session = dataset._session,
                dependencies = self._deps,
                drop_input_cols = self._drop_input_cols,
                expected_output_cols_type = expected_type_inferred,
            )

        elif isinstance(dataset, pd.DataFrame):
            transform_kwargs = dict(
                snowpark_input_cols = self._snowpark_cols,
                drop_input_cols = self._drop_input_cols
                )

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )

        output_df: DATAFRAME_TYPE = transform_handlers.batch_inference(
            inference_method=inference_method,
            input_cols=self.input_cols,
            expected_output_cols= self.output_cols,
            **transform_kwargs
        )

        return output_df

    @available_if(original_estimator_has_callable("transform"))  # type: ignore[misc]
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def transform(self, dataset: Union[DataFrame, pd.DataFrame]) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.

        Returns:
            Transformed dataset.
        """
        super()._check_dataset_type(dataset)
        inference_method="transform"

        # This dictionary contains optional kwargs for batch inference. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: BatchInferenceKwargsTypedDict = dict()
        if isinstance(dataset, DataFrame):
            expected_dtype = ""
            if False:  # is child of _BaseHeterogeneousEnsemble
                # transform() method of HeterogeneousEnsemble estimators return responses of varying shapes
                # from (n_samples, n_estimators) to (n_samples, n_estimators * n_classes) (and everything in between)
                # based on init param values. We will convert that to pandas dataframe of shape (n_samples, 1) with
                # each row containing a list of values.
                expected_dtype = "array"

            # If we were unable to assign a type to this transform in the factory, infer the type here.
            if expected_dtype == "":
                # If this is a clustering transformer, if the number of output columns does not equal the number of clusters the response will be an "array"
                if hasattr(self._sklearn_object, "n_clusters") and getattr(self._sklearn_object, "n_clusters") != len(self.output_cols):
                    expected_dtype = "array"
                # If this is a decomposition transformer, if the number of output columns does not equal the number of components the response will be an "array"
                elif hasattr(self._sklearn_object, "n_components") and getattr(self._sklearn_object, "n_components") != len(self.output_cols):
                    expected_dtype = "array"
                else:
                    output_types = [signature.as_snowpark_type() for signature in _infer_signature(dataset[self.input_cols], "output", use_snowflake_identifiers=True)]
                    # We can only infer the output types from the input types if the following two statemetns are true:
                    # 1) All of the output types are the same. Otherwise, we still have to fall back to variant because `_sklearn_inference` only accepts one type.
                    # 2) The length of the input columns equals the length of the output columns. Otherwise the transform will likely result in an `ARRAY`.
                    if all(x == output_types[0] for x in output_types) and len(output_types) == len(self.output_cols):
                        expected_dtype = convert_sp_to_sf_type(output_types[0])
            
            self._deps = self._batch_inference_validate_snowpark(
                dataset=dataset,
                inference_method=inference_method,
            )
            assert isinstance(dataset._session, Session) # mypy does not recognize the check in _batch_inference_validate_snowpark()

            transform_kwargs = dict(
                session = dataset._session,
                dependencies = self._deps,
                drop_input_cols = self._drop_input_cols,
                expected_output_cols_type = expected_dtype,
            )

        elif isinstance(dataset, pd.DataFrame):
            transform_kwargs = dict(
                snowpark_input_cols = self._snowpark_cols,
                drop_input_cols = self._drop_input_cols
                )

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )

        output_df: DATAFRAME_TYPE = transform_handlers.batch_inference(
            inference_method=inference_method,
            input_cols=self.input_cols,
            expected_output_cols=self.output_cols,
            **transform_kwargs
        )
        return output_df
    
    @available_if(original_estimator_has_callable("fit_predict"))  # type: ignore[misc]
    def fit_predict(self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "fit_predict_",) -> Union[DataFrame, pd.DataFrame]:
        """ Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
        output_cols_prefix: Prefix for the response columns
        Returns:
            Predicted dataset.
        """
        self._infer_input_output_cols(dataset)
        super()._check_dataset_type(dataset)
        model_trainer = ModelTrainerBuilder.build_fit_predict(
            estimator=self._sklearn_object,
            dataset=dataset,
            input_cols=self.input_cols,
            autogenerated=self._autogenerated,
            subproject=_SUBPROJECT,
        )
        output_result, fitted_estimator = model_trainer.train_fit_predict(
            drop_input_cols=self._drop_input_cols,
            expected_output_cols_list=self.output_cols if self.output_cols else self._get_output_column_names(output_cols_prefix),
        )
        self._sklearn_object = fitted_estimator
        self._is_fitted = True
        return output_result


    @available_if(_is_fit_transform_method_enabled())  # type: ignore[misc]
    def fit_transform(self, dataset: Union[DataFrame, pd.DataFrame]) -> Union[Any, npt.NDArray[Any]]:
        """ 
        Returns:
            Transformed dataset.
        """
        self.fit(dataset)
        assert self._sklearn_object is not None
        return self._sklearn_object.embedding_

    @available_if(original_estimator_has_callable("predict_proba"))  # type: ignore[misc]
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def predict_proba(
        self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "predict_proba_"
    ) -> Union[DataFrame, pd.DataFrame]:
        """Probability estimates
        For more details on this function, see [sklearn.neural_network.MLPClassifier.predict_proba]
        (https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier.predict_proba)


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: Prefix for the response columns

        Returns:
            Output dataset with probability of the sample for each class in the model.
        """
        super()._check_dataset_type(dataset)
        inference_method = "predict_proba"

        # This dictionary contains optional kwargs for batch inference. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: BatchInferenceKwargsTypedDict = dict() 

        if isinstance(dataset, DataFrame):
            self._deps = self._batch_inference_validate_snowpark(
                dataset=dataset,
                inference_method=inference_method,
            )
            assert isinstance(dataset._session, Session) # mypy does not recognize the check in _batch_inference_validate_snowpark()
            transform_kwargs = dict(
                session=dataset._session,
                dependencies=self._deps,
                drop_input_cols = self._drop_input_cols,
                expected_output_cols_type="float",
            )

        elif isinstance(dataset, pd.DataFrame):
            transform_kwargs = dict(
                snowpark_input_cols = self._snowpark_cols,
                drop_input_cols = self._drop_input_cols
                )

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )
        output_df: DATAFRAME_TYPE = transform_handlers.batch_inference(
            inference_method=inference_method,
            input_cols=self.input_cols,
            expected_output_cols=self._get_output_column_names(output_cols_prefix),
            **transform_kwargs
        )
        return output_df

    @available_if(original_estimator_has_callable("predict_log_proba"))  # type: ignore[misc]
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def predict_log_proba(
        self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "predict_log_proba_"
    ) -> Union[DataFrame, pd.DataFrame]:
        """Probability estimates
        For more details on this function, see [sklearn.neural_network.MLPClassifier.predict_proba]
        (https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier.predict_proba)


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: str
                Prefix for the response columns

        Returns:
            Output dataset with log probability of the sample for each class in the model.
        """
        super()._check_dataset_type(dataset)
        inference_method="predict_log_proba"

        # This dictionary contains optional kwargs for batch inference. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: BatchInferenceKwargsTypedDict = dict()  

        if isinstance(dataset, DataFrame):
            self._deps = self._batch_inference_validate_snowpark(
                dataset=dataset,
                inference_method=inference_method,
            )
            assert isinstance(dataset._session, Session) # mypy does not recognize the check in _batch_inference_validate_snowpark()
            transform_kwargs = dict(
                session=dataset._session,
                dependencies=self._deps,
                drop_input_cols = self._drop_input_cols,
                expected_output_cols_type="float",
            )
        elif isinstance(dataset, pd.DataFrame):
            transform_kwargs = dict(
                snowpark_input_cols = self._snowpark_cols,
                drop_input_cols = self._drop_input_cols
                )

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )

        output_df: DATAFRAME_TYPE = transform_handlers.batch_inference(
            inference_method=inference_method,
            input_cols=self.input_cols,
            expected_output_cols=self._get_output_column_names(output_cols_prefix),
            **transform_kwargs
        )
        return output_df


    @available_if(original_estimator_has_callable("decision_function"))  # type: ignore[misc]
    def decision_function(
        self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "decision_function_"
    ) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: str
                Prefix for the response columns

        Returns:
            Output dataset with results of the decision function for the samples in input dataset.
        """
        super()._check_dataset_type(dataset)
        inference_method="decision_function"

        # This dictionary contains optional kwargs for batch inference. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: BatchInferenceKwargsTypedDict = dict()  

        if isinstance(dataset, DataFrame):
            self._deps = self._batch_inference_validate_snowpark(
                dataset=dataset,
                inference_method=inference_method,
            )
            assert isinstance(dataset._session, Session) # mypy does not recognize the check in _batch_inference_validate_snowpark()
            transform_kwargs = dict(
                session=dataset._session,
                dependencies=self._deps,
                drop_input_cols = self._drop_input_cols,
                expected_output_cols_type="float",
            )

        elif isinstance(dataset, pd.DataFrame):
            transform_kwargs = dict(
                snowpark_input_cols = self._snowpark_cols,
                drop_input_cols = self._drop_input_cols
                )

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )

        output_df: DATAFRAME_TYPE = transform_handlers.batch_inference(
            inference_method=inference_method,
            input_cols=self.input_cols,
            expected_output_cols=self._get_output_column_names(output_cols_prefix),
            **transform_kwargs
        )
        return output_df

    @available_if(original_estimator_has_callable("score_samples"))  # type: ignore[misc]
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def score_samples(
        self, dataset: Union[DataFrame, pd.DataFrame], output_cols_prefix: str = "score_samples_"
    ) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: Prefix for the response columns

        Returns:
            Output dataset with probability of the sample for each class in the model.
        """
        super()._check_dataset_type(dataset)
        inference_method="score_samples"

        # This dictionary contains optional kwargs for batch inference. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: BatchInferenceKwargsTypedDict = dict()

        if isinstance(dataset, DataFrame):
            self._deps = self._batch_inference_validate_snowpark(
                dataset=dataset,
                inference_method=inference_method,
            )
            assert isinstance(dataset._session, Session) # mypy does not recognize the check in _batch_inference_validate_snowpark()
            transform_kwargs = dict(
                session=dataset._session,
                dependencies=self._deps,
                drop_input_cols = self._drop_input_cols,
                expected_output_cols_type="float",
            )

        elif isinstance(dataset, pd.DataFrame):
            transform_kwargs = dict(
                snowpark_input_cols = self._snowpark_cols,
                drop_input_cols = self._drop_input_cols
                )

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )

        output_df: DATAFRAME_TYPE = transform_handlers.batch_inference(
            inference_method=inference_method,
            input_cols=self.input_cols,
            expected_output_cols=self._get_output_column_names(output_cols_prefix),
            **transform_kwargs
        )
        return output_df

    @available_if(original_estimator_has_callable("score"))  # type: ignore[misc]
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def score(self, dataset: Union[DataFrame, pd.DataFrame]) -> float:
        """Return the mean accuracy on the given test data and labels
        For more details on this function, see [sklearn.neural_network.MLPClassifier.score]
        (https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html#sklearn.neural_network.MLPClassifier.score)


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.

        Returns:
            Score.
        """
        self._infer_input_output_cols(dataset)
        super()._check_dataset_type(dataset)

        # This dictionary contains optional kwargs for scoring. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: ScoreKwargsTypedDict = dict()  

        if isinstance(dataset, DataFrame):
            self._deps = self._batch_inference_validate_snowpark(
                dataset=dataset,
                inference_method="score",
            )
            selected_cols = self._get_active_columns()
            if len(selected_cols) > 0:
                dataset = dataset.select(selected_cols)
            assert isinstance(dataset._session, Session) # keep mypy happy
            transform_kwargs = dict(
                session=dataset._session,
                dependencies=["snowflake-snowpark-python"] + self._deps,
                score_sproc_imports=['sklearn'],
            )
        elif isinstance(dataset, pd.DataFrame):
            # pandas_handler.score() does not require any extra kwargs.
            transform_kwargs = dict()

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )

        output_score = transform_handlers.score(
            input_cols=self.input_cols,
            label_cols=self.label_cols,
            sample_weight_col=self.sample_weight_col,
            **transform_kwargs
        )

        return output_score


    @available_if(original_estimator_has_callable("kneighbors"))  # type: ignore[misc]
    @telemetry.send_api_usage_telemetry(
        project=_PROJECT,
        subproject=_SUBPROJECT,
        custom_tags=dict([("autogen", True)]),
    )
    def kneighbors(
        self,
        dataset: Union[DataFrame, pd.DataFrame],
        n_neighbors: Optional[int] = None,
        return_distance: bool = True,
        output_cols_prefix: str = "kneighbors_",
    ) -> Union[DataFrame, pd.DataFrame]:
        """Method not supported for this class.


        Raises:
            TypeError: Supported dataset types: snowpark.DataFrame, pandas.DataFrame.

        Args:
            dataset: Union[snowflake.snowpark.DataFrame, pandas.DataFrame]
                Snowpark or Pandas DataFrame.
            output_cols_prefix: str
                Prefix for the response columns

        Returns:
            Output dataset with results of the K-neighbors for the samples in input dataset.
        """
        super()._check_dataset_type(dataset)
        inference_method="kneighbors"

        # This dictionary contains optional kwargs for batch inference. These kwargs
        # are specific to the type of dataset used. 
        transform_kwargs: BatchInferenceKwargsTypedDict = dict() 
        output_cols = ["neigh_ind"]
        if return_distance:
            output_cols.insert(0, "neigh_dist")

        if isinstance(dataset, DataFrame):

            self._deps = self._batch_inference_validate_snowpark(
                dataset=dataset,
                inference_method=inference_method,

            )
            assert isinstance(dataset._session, Session) # mypy does not recognize the check in _batch_inference_validate_snowpark()
            transform_kwargs = dict(
                session = dataset._session,
                dependencies = self._deps,
                drop_input_cols = self._drop_input_cols,
                expected_output_cols_type="array",
                n_neighbors = n_neighbors,
                return_distance =  return_distance
            )
        elif isinstance(dataset, pd.DataFrame):
            transform_kwargs = dict(
                n_neighbors = n_neighbors,
                return_distance = return_distance,
                snowpark_input_cols = self._snowpark_cols
            )

        transform_handlers = ModelTransformerBuilder.build(
            dataset=dataset,
            estimator=self._sklearn_object,
            class_name=self._class_name,
            subproject=self._subproject,
            autogenerated=self._autogenerated
        )

        output_df: DATAFRAME_TYPE = transform_handlers.batch_inference(
            inference_method=inference_method,
            input_cols=self.input_cols,
            expected_output_cols=self._get_output_column_names(output_cols_prefix, output_cols),
            **transform_kwargs
        )
        return output_df


    def _get_model_signatures(self, dataset: Union[DataFrame, pd.DataFrame]) -> None:
        self._model_signature_dict = dict()

        PROB_FUNCTIONS = ["predict_log_proba", "predict_proba", "decision_function"]

        inputs = list(_infer_signature(dataset[self.input_cols], "input"))
        outputs: List[BaseFeatureSpec] = []
        if hasattr(self, "predict"):
            # keep mypy happy
            assert self._sklearn_object is not None and hasattr(self._sklearn_object, "_estimator_type") 
            # For classifier, the type of predict is the same as the type of label
            if self._sklearn_object._estimator_type == 'classifier':
                 # label columns is the desired type for output
                outputs = list(_infer_signature(dataset[self.label_cols], "output", use_snowflake_identifiers=True))
                # rename the output columns
                outputs = list(model_signature_utils.rename_features(outputs, self.output_cols))
                self._model_signature_dict["predict"] = ModelSignature(inputs,
                                                                       ([] if self._drop_input_cols else inputs)
                                                                       + outputs)
            # For mixture models that use the density mixin, `predict` returns the argmax of the log prob.
            # For outlier models, returns -1 for outliers and 1 for inliers.
            # Clusterer returns int64 cluster labels. 
            elif self._sklearn_object._estimator_type in ["DensityEstimator", "clusterer", "outlier_detector"]:
                outputs = [FeatureSpec(dtype=DataType.INT64, name=c) for c in self.output_cols]
                self._model_signature_dict["predict"] = ModelSignature(inputs,
                                                                       ([] if self._drop_input_cols else inputs)
                                                                       + outputs)
            
            # For regressor, the type of predict is float64
            elif self._sklearn_object._estimator_type == 'regressor':
                outputs = [FeatureSpec(dtype=DataType.DOUBLE, name=c) for c in self.output_cols]
                self._model_signature_dict["predict"] = ModelSignature(inputs,
                                                                       ([] if self._drop_input_cols else inputs)
                                                                       + outputs)
                
        for prob_func in PROB_FUNCTIONS:
            if hasattr(self, prob_func):
                output_cols_prefix: str = f"{prob_func}_"
                output_column_names = self._get_output_column_names(output_cols_prefix)
                outputs = [FeatureSpec(dtype=DataType.DOUBLE, name=c) for c in output_column_names]
                self._model_signature_dict[prob_func] = ModelSignature(inputs,
                                                                       ([] if self._drop_input_cols else inputs)
                                                                       + outputs)

        # Output signature names may still need to be renamed, since they were not created with `_infer_signature`.
        items = list(self._model_signature_dict.items())
        for method, signature in items:
            signature._outputs = _rename_signature_with_snowflake_identifiers(signature._outputs)
            self._model_signature_dict[method] = signature

    @property
    def model_signatures(self) -> Dict[str, ModelSignature]:
        """Returns model signature of current class.

        Raises:
            exceptions.SnowflakeMLException: If estimator is not fitted, then model signature cannot be inferred

        Returns:
            Dict[str, ModelSignature]: each method and its input output signature
        """
        if self._model_signature_dict is None:
            raise exceptions.SnowflakeMLException(
                error_code=error_codes.INVALID_ATTRIBUTE,
                original_exception=RuntimeError("Estimator not fitted before accessing property model_signatures!"),
            )
        return self._model_signature_dict

    def to_sklearn(self) -> Any:
        """Get sklearn.neural_network.MLPClassifier object.
        """
        if self._sklearn_object is None:
            self._sklearn_object = self._create_sklearn_object()
        return self._sklearn_object

    def to_xgboost(self) -> Any:
        raise exceptions.SnowflakeMLException(
            error_code=error_codes.METHOD_NOT_ALLOWED,
            original_exception=AttributeError(
                modeling_error_messages.UNSUPPORTED_MODEL_CONVERSION.format(
                    "to_xgboost()", 
                    "to_sklearn()"
                )
            ),
        )

    def to_lightgbm(self) -> Any:
        raise exceptions.SnowflakeMLException(
            error_code=error_codes.METHOD_NOT_ALLOWED,
            original_exception=AttributeError(
                modeling_error_messages.UNSUPPORTED_MODEL_CONVERSION.format(
                    "to_lightgbm()", 
                    "to_sklearn()"
                )
            ),
        )

    def _get_dependencies(self) -> List[str]:
        return self._deps
