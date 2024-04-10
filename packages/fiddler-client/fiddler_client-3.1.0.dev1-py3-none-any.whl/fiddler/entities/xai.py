from __future__ import annotations

import os
from collections import namedtuple
from io import BytesIO
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

import pandas as pd

from fiddler.constants.dataset import EnvType
from fiddler.constants.xai import ExplainMethod
from fiddler.decorators import handle_api_error
from fiddler.entities.job import Job
from fiddler.schemas.job import JobCompactResp
from fiddler.schemas.xai import (
    DatasetDataSource,
    EventIdDataSource,
    RowDataSource,
    SqlSliceQueryDataSource,
)
from fiddler.utils.helpers import try_series_retype
from fiddler.utils.logger import get_logger

logger = get_logger(__name__)


class XaiMixin:
    id: UUID | None
    _client: Callable

    def _get_method(self, update: bool = False) -> Callable:
        """Get HTTP method"""
        return self._client().put if update else self._client().post

    @handle_api_error
    def explain(  # pylint: disable=too-many-arguments
        self,
        input_data_source: RowDataSource | EventIdDataSource,
        ref_data_source: DatasetDataSource | SqlSliceQueryDataSource | None = None,
        method: ExplainMethod | str = ExplainMethod.FIDDLER_SHAP,
        num_permutations: int | None = None,
        ci_level: float | None = None,
        top_n_class: int | None = None,
    ) -> tuple:
        """
        Get explanation for a single observation.

        :param input_data_source: DataSource for the input data to compute explanation
            on (RowDataSource, EventIdDataSource)
        :param ref_data_source: DataSource for the reference data to compute explanation
            on (DatasetDataSource, SqlSliceQueryDataSource).
            Only used for non-text models and the following methods:
            'SHAP', 'FIDDLER_SHAP', 'PERMUTE', 'MEAN_RESET'
        :param method: Explanation method name. Could be your custom
            explanation method or one of the following method:
            'SHAP', 'FIDDLER_SHAP', 'IG', 'PERMUTE', 'MEAN_RESET', 'ZERO_RESET'
        :param num_permutations: For Fiddler SHAP, that corresponds to the number of
            coalitions to sample to estimate the Shapley values of each single-reference
             game. For the permutation algorithms, this corresponds to the number
            of permutations from the dataset to use for the computation.
        :param ci_level: The confidence level (between 0 and 1) to use for the
            confidence intervals in Fiddler SHAP. Not used for other methods.
        :param top_n_class: For multiclass classification models only, specifying if
            only the n top classes are computed or all classes (when parameter is None)

        :return: A named tuple with the explanation results.
        """
        self._check_id_attributes()
        payload: dict[str, Any] = {
            'model_id': self.id,
            'input_data_source': input_data_source.dict(),
            'explanation_type': method,
        }
        if ref_data_source:
            payload['ref_data_source'] = ref_data_source.dict(exclude_none=True)
        if num_permutations:
            payload['num_permutations'] = num_permutations
        if ci_level:
            payload['ci_level'] = ci_level
        if top_n_class:
            payload['top_n_class'] = top_n_class

        response = self._client().post(
            url='v3/explain',
            data=payload,
        )

        return namedtuple('Explain', response.json()['data'])(**response.json()['data'])

    @handle_api_error
    def get_fairness(
        self,
        data_source: DatasetDataSource | SqlSliceQueryDataSource,
        protected_features: list[str],
        positive_outcome: str | int | float | bool,
        score_threshold: float | None = None,
    ) -> tuple:
        """
        Get fairness analysis on a dataset or a slice.

        :param data_source: DataSource for the input dataset to compute
            fairness on (DatasetDataSource or SqlSliceQueryDataSource)
        :param protected_features: list of protected attribute names to compute
            Fairness analysis on
        :param positive_outcome: name of the positive outcome to compute
            Fairness analysis on
        :param score_threshold: Binary threshold value (between 0 and 1). Default to 0.5

        :return: A named tuple with the fairness results.
        """
        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'data_source': data_source.dict(exclude_none=True),
            'protected_features': protected_features,
            'positive_outcome': positive_outcome,
        }
        if score_threshold:
            payload['score_threshold'] = score_threshold

        response = self._client().post(url='/v3/analytics/fairness', data=payload)

        return namedtuple('Fairness', response.json()['data'])(
            **response.json()['data']
        )

    @handle_api_error
    def get_slice(
        self,
        query: str,
        sample: bool = False,
        max_rows: int | None = None,
        columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Fetch data with slice query.

        :param query: An SQL query that begins with the keyword 'SELECT'
        :param columns: Allows caller to explicitly specify list of
                        columns to select overriding columns selected in the query.
        :param max_rows: Number of maximum rows to fetch
        :param sample: Whether rows should be sample or not from the database

        :return: Dataframe of the query output
        """
        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'query': query,
            'sample': sample,
        }
        if max_rows:
            payload['max_rows'] = max_rows
        if columns:
            payload['columns'] = columns

        response = self._client().post(
            url='/v3/slice-query/fetch',
            data=payload,
        )

        response_dict = response.json()['data']

        column_names = response_dict['metadata']['columns']
        dtype_strings = response_dict['metadata']['dtypes']
        df = pd.DataFrame(response_dict['rows'], columns=column_names)
        for column_name, dtype in zip(column_names, dtype_strings):
            df[column_name] = try_series_retype(df[column_name], dtype)
        return df

    @handle_api_error
    def download_slice(  # pylint: disable=too-many-arguments
        self,
        output_dir: Path | str,
        query: str,
        sample: bool = False,
        max_rows: int | None = None,
        columns: list[str] | None = None,
    ) -> None:
        """
        Download data with slice query to parquet file.

        :param output_dir: Path to download the file
        :param query: An SQL query that begins with the keyword 'SELECT'
        :param columns: Allows caller to explicitly specify list of
                        columns to select overriding columns selected in the query.
        :param max_rows: Number of maximum rows to fetch
        :param sample: Whether rows should be sample or not from the database
        """
        self._check_id_attributes()
        output_dir = Path(output_dir)
        if not output_dir.exists():
            os.makedirs(output_dir)
        payload: dict[str, Any] = {
            'model_id': self.id,
            'query': query,
            'sample': sample,
        }
        if max_rows:
            payload['max_rows'] = max_rows
        if columns:
            payload['columns'] = columns

        file_path = os.path.join(output_dir, 'output.parquet')
        with self._client().post(url='/v3/slice-query/download', data=payload) as resp:
            # Download parquet file
            df = pd.read_parquet(BytesIO(resp.content))
            df.to_parquet(file_path)

    @handle_api_error
    def get_mutual_info(
        self,
        query: str,
        column_name: str,
        num_samples: int | None = None,
        normalized: bool = False,
    ) -> dict:
        """
        Get mutual information.

        The Mutual information measures the dependency between
        two random variables. It's a non-negative value. If two random variables are
        independent MI is equal to zero. Higher MI values means higher dependency.

        :param query: slice query to compute Mutual information on
        :param column_name: column name to compute mutual information with respect to
               all the variables in the dataset.
        :param num_samples: Number of samples to select for computation
        :param normalized: If set to True, it will compute Normalized Mutual Information

        :return: a dictionary of mutual information w.r.t the given feature
                 for each column given
        """
        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'query': query,
            'column_name': column_name,
            'normalized': normalized,
        }
        if num_samples:
            payload['num_samples'] = num_samples

        response = self._client().post(
            url='/v3/analytics/mutual-info',
            data=payload,
        )

        return response.json()['data']

    @handle_api_error
    def predict(
        self,
        df: pd.DataFrame,
        chunk_size: int | None = None,
    ) -> pd.DataFrame:
        """
        Run model on an input dataframe.

        :param df: Feature dataframe
        :param chunk_size: Chunk size for fetching predictions

        :return: Dataframe of the predictions
        """
        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'data': df.to_dict('records'),
        }
        if chunk_size:
            payload['chunk_size'] = chunk_size

        response = self._client().post(
            url='/v3/predict',
            data=payload,
        )
        return pd.DataFrame(response.json()['data']['predictions'])

    @handle_api_error
    def get_feature_impact(  # pylint: disable=too-many-arguments
        self,
        data_source: DatasetDataSource | SqlSliceQueryDataSource,
        num_iterations: int | None = None,
        num_refs: int | None = None,
        ci_level: float | None = None,
        min_support: int | None = None,
        output_columns: list[str] | None = None,
    ) -> tuple:
        """
        Get global feature impact for a model over a dataset or a slice.

        :param data_source: DataSource for the input dataset to compute feature
            impact on (DatasetDataSource or SqlSliceQueryDataSource)
        :param num_iterations: The maximum number of ablated model inferences per feature
        :param num_refs: The number of reference points used in the explanation
        :param ci_level: The confidence level (between 0 and 1)
        :param min_support: Only used for NLP (TEXT inputs) models. Specify a minimum
            support (number of times a specific word was present in the sample data)
            to retrieve top words. Default to 15.
        :param output_columns: Only used for NLP (TEXT inputs) models. Output column
            names to compute feature impact on.

        :return: Feature Impact tuple
        """

        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'data_source': data_source.dict(exclude_none=True),
        }

        if num_refs:
            payload['num_refs'] = num_refs
        if num_iterations:
            payload['num_iterations'] = num_iterations
        if ci_level:
            payload['ci_level'] = ci_level
        if min_support:
            payload['min_support'] = min_support
        if output_columns:
            payload['output_columns'] = output_columns

        response = self._client().post(
            url='/v3/analytics/feature-impact',
            data=payload,
        )

        return namedtuple('FeatureImpact', response.json()['data'])(
            **response.json()['data']
        )

    @handle_api_error
    def get_feature_importance(  # pylint: disable=too-many-arguments
        self,
        data_source: DatasetDataSource | SqlSliceQueryDataSource,
        num_iterations: int | None = None,
        num_refs: int | None = None,
        ci_level: float | None = None,
    ) -> tuple:
        """
        Get global feature importance for a model over a dataset or a slice.

        :param data_source: DataSource for the input dataset to compute feature
            importance on (DatasetDataSource or SqlSliceQueryDataSource)
        :param num_iterations: The maximum number of ablated model inferences per feature
        :param num_refs: The number of reference points used in the explanation
        :param ci_level: The confidence level (between 0 and 1)

        :return: Feature Importance tuple
        """

        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'data_source': data_source.dict(),
        }

        if num_refs:
            payload['num_refs'] = num_refs
        if num_iterations:
            payload['num_iterations'] = num_iterations
        if ci_level:
            payload['ci_level'] = ci_level

        response = self._client().post(
            url='/v3/analytics/feature-importance',
            data=payload,
        )

        return namedtuple('FeatureImportance', response.json()['data'])(
            **response.json()['data']
        )

    @handle_api_error
    def precompute_feature_impact(  # pylint: disable=too-many-arguments
        self,
        dataset_id: UUID | str,
        num_samples: int | None = None,
        num_iterations: int | None = None,
        num_refs: int | None = None,
        ci_level: float | None = None,
        min_support: int | None = None,
        update: bool = False,
    ) -> Job:
        """Pre-compute feature impact for a model on a dataset.

        This is used in various places in the UI.
        A single feature impact can be precomputed (computed and cached) for a model.

        :param dataset_id: The unique identifier of the dataset
        :param num_samples: The number of samples used
        :param num_iterations: The maximum number of ablated model inferences per feature
        :param num_refs: The number of reference points used in the explanation
        :param ci_level: The confidence level (between 0 and 1)
        :param min_support: Only used for NLP (TEXT inputs) models. Specify a minimum
            support (number of times a specific word was present in the sample data)
            to retrieve top words. Default to 15.
        :param update: Whether the precomputed feature impact should be recomputed and updated

        :return: Async Job
        """

        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'env_id': dataset_id,
            'env_type': EnvType.PRE_PRODUCTION,
        }
        if num_samples:
            payload['num_samples'] = num_samples
        if num_refs:
            payload['num_refs'] = num_refs
        if num_iterations:
            payload['num_iterations'] = num_iterations
        if ci_level:
            payload['ci_level'] = ci_level
        if min_support:
            payload['min_support'] = min_support

        method = self._get_method(update)

        response = method(
            url='/v3/analytics/precompute-feature-impact',
            data=payload,
        )

        job_compact = JobCompactResp(**response.json()['data']['job'])
        logger.info(
            'Model[%s] - Submitted job (%s) for precomputing feature impact',
            self.id,
            job_compact.id,
        )
        return Job.get(id_=job_compact.id)

    @handle_api_error
    def precompute_feature_importance(  # pylint: disable=too-many-arguments
        self,
        dataset_id: UUID | str,
        num_samples: int | None = None,
        num_iterations: int | None = None,
        num_refs: int | None = None,
        ci_level: float | None = None,
        update: bool = False,
    ) -> Job:
        """Pre-compute feature importance for a model on a dataset.

        This is used in various places in the UI.
        A single feature importance can be precomputed (computed and cached) for a model.

        :param dataset_id: The unique identifier of the dataset
        :param num_samples: The number of samples used
        :param num_iterations: The maximum number of ablated model inferences per feature
        :param num_refs: The number of reference points used in the explanation
        :param ci_level: The confidence level (between 0 and 1)
        :param update: Whether the precomputed feature impact should be recomputed and updated

        :return: Async Job
        """

        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'env_id': dataset_id,
            'env_type': EnvType.PRE_PRODUCTION,
        }
        if num_samples:
            payload['num_samples'] = num_samples
        if num_refs:
            payload['num_refs'] = num_refs
        if num_iterations:
            payload['num_iterations'] = num_iterations
        if ci_level:
            payload['ci_level'] = ci_level

        method = self._get_method(update)

        response = method(
            url='/v3/analytics/precompute-feature-importance',
            data=payload,
        )

        job_compact = JobCompactResp(**response.json()['data']['job'])
        logger.info(
            'Model[%s] - Submitted job (%s) for precomputing feature importance',
            self.id,
            job_compact.id,
        )
        return Job.get(id_=job_compact.id)

    @handle_api_error
    def get_precomputed_feature_importance(self) -> tuple:
        """Get precomputed feature importance for a model"""

        self._check_id_attributes()
        response = self._client().post(
            url='/v3/analytics/feature-importance/precomputed',
            data={'model_id': self.id},
        )

        return namedtuple('FeatureImportance', response.json()['data'])(
            **response.json()['data']
        )

    @handle_api_error
    def get_precomputed_feature_impact(self) -> tuple:
        """Get precomputed feature impact for a model"""

        self._check_id_attributes()
        response = self._client().post(
            url='/v3/analytics/feature-impact/precomputed',
            data={'model_id': self.id},
        )

        return namedtuple('FeatureImpact', response.json()['data'])(
            **response.json()['data']
        )

    @handle_api_error
    def precompute_predictions(
        self,
        dataset_id: UUID | str,
        chunk_size: int | None = None,
        update: bool = False,
    ) -> Job:
        """
        Pre-compute predictions for a model on a dataset

        :param dataset_id: The unique identifier of the dataset
        :param chunk_size: Chunk size for fetching predictions
        :param update: Whether the pre-computed predictions should be re-computed and updated for this dataset

        :return: Dataframe of the predictions
        """
        self._check_id_attributes()

        payload: dict[str, Any] = {
            'model_id': self.id,
            'env_id': dataset_id,
        }

        if chunk_size:
            payload['batch_size'] = chunk_size

        method = self._get_method(update)

        response = method(
            url='/v3/analytics/precompute-predictions',
            data=payload,
        )

        job_compact = JobCompactResp(**response.json()['data']['job'])
        logger.info(
            'Model[%s] - Submitted job (%s) for precomputing predictions on dataset[%s]',
            self.id,
            job_compact.id,
            dataset_id,
        )
        return Job.get(id_=job_compact.id)

    def _check_id_attributes(self) -> None:
        if not self.id:
            raise AttributeError(
                'This method is available only for model object generated from '
                'API response.'
            )
