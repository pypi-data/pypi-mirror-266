import io
import os
import shutil
from collections import namedtuple

import pandas as pd
import responses

from fiddler.entities.job import Job
from fiddler.entities.model import Model
from fiddler.schemas.xai import DatasetDataSource, RowDataSource
from fiddler.tests.constants import (
    BASE_TEST_DIR,
    DATASET_ID,
    DATASET_NAME,
    JOB_ID,
    MODEL_ID,
    MODEL_NAME,
    MODEL_VERSION,
    ORG_ID,
    ORG_NAME,
    OUTPUT_DIR,
    PROJECT_ID,
    PROJECT_NAME,
    URL,
    USER_EMAIL,
    USER_ID,
    USER_NAME,
)

MODEL_SCHEMA = {
    'columns': [
        {
            'bins': [
                350.0,
                400.0,
                450.0,
                500.0,
                550.0,
                600.0,
                650.0,
                700.0,
                750.0,
                800.0,
                850.0,
            ],
            'categories': None,
            'data_type': 'int',
            'id': 'creditscore',
            'max': 850,
            'min': 350,
            'n_dimensions': None,
            'name': 'CreditScore',
            'replace_with_nulls': None,
        },
    ],
    'schema_version': 1,
}
MODEL_SPEC = {
    'custom_features': [],
    'decisions': ['Decisions'],
    'inputs': [
        'CreditScore',
    ],
    'metadata': [],
    'outputs': ['probability_churned'],
    'schema_version': 1,
    'targets': ['Churned'],
}
MODEL_API_RESPONSE_200 = {
    'data': {
        'id': MODEL_ID,
        'name': MODEL_NAME,
        'version': MODEL_VERSION,
        'project': {
            'id': PROJECT_ID,
            'name': PROJECT_NAME,
        },
        'organization': {
            'id': ORG_ID,
            'name': ORG_NAME,
        },
        'input_type': 'structured',
        'task': 'binary_classification',
        'task_params': {
            'binary_classification_threshold': 0.5,
            'target_class_order': ['Not Churned', 'Churned'],
            'group_by': None,
            'top_k': None,
            'class_weights': None,
            'weighted_ref_histograms': None,
        },
        'schema': MODEL_SCHEMA,
        'spec': MODEL_SPEC,
        'description': 'This model predicts whether customer stays or churns',
        'event_id_col': None,
        'event_ts_col': None,
        'event_ts_format': None,
        'xai_params': {
            'custom_explain_methods': [],
            'default_explain_method': None,
        },
        'artifact_status': 'no_model',
        'artifact_files': [],
        'created_at': '2023-11-22 16:50:57.705784',
        'updated_at': '2023-11-22 16:50:57.705784',
        'created_by': {
            'id': USER_ID,
            'full_name': USER_NAME,
            'email': USER_EMAIL,
        },
        'updated_by': {
            'id': USER_ID,
            'full_name': USER_NAME,
            'email': USER_EMAIL,
        },
        'input_cols': [
            MODEL_SCHEMA['columns'][0],
            MODEL_SCHEMA['columns'][0],
        ],
        'output_cols': [MODEL_SCHEMA['columns'][0]],
        'target_cols': [MODEL_SCHEMA['columns'][0]],
        'metadata_cols': [],
        'decision_cols': [MODEL_SCHEMA['columns'][0]],
        'is_binary_ranking_model': False,
    },
}

EXPLAIN_RESPONSE_200 = {
    'data': {
        'explanation_type': 'FIDDLER_SHAP',
        'num_permutations': 50,
        'ci_level': 0.95,
        'explanations': {
            'probability_churned': {
                'model_prediction': 0.40507614012286625,
                'baseline_prediction': 0.19293562908483303,
                'GEM': {
                    'type': 'container',
                    'contents': [
                        {
                            'type': 'simple',
                            'feature-name': 'CreditScore',
                            'value': 619,
                            'attribution': -0.022117800470630538,
                            'attribution-uncertainty': 0.006245936205277383,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'Geography',
                            'value': 'France',
                            'attribution': 0.028808698749482956,
                            'attribution-uncertainty': 0.008490776240161464,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'Gender',
                            'value': 'Female',
                            'attribution': 0.059352095878178614,
                            'attribution-uncertainty': 0.010825591198269912,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'Age',
                            'value': 42,
                            'attribution': 0.04663932271153231,
                            'attribution-uncertainty': 0.026679728117630943,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'Tenure',
                            'value': 2,
                            'attribution': 0.012244800190215574,
                            'attribution-uncertainty': 0.006979182051724819,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'Balance',
                            'value': 0.0,
                            'attribution': 0.08161626352219709,
                            'attribution-uncertainty': 0.017052188444913206,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'NumOfProducts',
                            'value': 1,
                            'attribution': 0.038190793675380155,
                            'attribution-uncertainty': 0.0582498509252494,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'HasCrCard',
                            'value': 'Yes',
                            'attribution': 0.00654585439939201,
                            'attribution-uncertainty': 0.004515983491581958,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'IsActiveMember',
                            'value': 'Yes',
                            'attribution': -0.05122940826721414,
                            'attribution-uncertainty': 0.013359099976724447,
                        },
                        {
                            'type': 'simple',
                            'feature-name': 'EstimatedSalary',
                            'value': 101348.88,
                            'attribution': 0.012089890649499193,
                            'attribution-uncertainty': 0.004951759795660022,
                        },
                    ],
                    'attribution': 0.21214051103803322,
                },
            },
        },
        'num_refs': 30,
    },
    'api_version': '3.0',
    'kind': 'NORMAL',
}

FAIRNESS_RESPONSE_200 = {
    'data': {
        'protected_attributes': ['Gender'],
        'label_distribution': {
            'columns': ['Gender', 'data_label', 'count'],
            'labels': [
                ['Female', 'Churned', 79],
                ['Female', 'Not Churned', 377],
                ['Male', 'Churned', 39],
                ['Male', 'Not Churned', 505],
            ],
        },
        'model_outcomes': {
            'columns': ['Gender', 'model_outcome', 'count'],
            'outcomes': [
                ['Female', 'Churned', 51],
                ['Female', 'Not Churned', 405],
                ['Male', 'Churned', 28],
                ['Male', 'Not Churned', 516],
            ],
        },
        'technical_metrics': {
            'columns': [
                'Gender',
                'true_positive_rate',
                'false_positive_rate',
                'true_negative_rate',
                'false_negative_rate',
                'false_omission_rate',
                'false_discovery_rate',
            ],
            'values': [
                [
                    'Female',
                    0.569620253164557,
                    0.015915119363395226,
                    0.9840848806366048,
                    0.43037974683544306,
                    0.08395061728395062,
                    0.11764705882352941,
                ],
                [
                    'Male',
                    0.5897435897435898,
                    0.009900990099009901,
                    0.9900990099009901,
                    0.41025641025641024,
                    0.031007751937984496,
                    0.17857142857142858,
                ],
            ],
        },
        'fairness_metrics': {
            'demographic_parity': {
                'index': ['dp'],
                'columns': ['Female', 'Male'],
                'data': [[0.1118421052631579, 0.051470588235294115]],
                'ratio': 0.4602076124567474,
            },
            'equal_opportunity': {
                'index': ['tpr'],
                'columns': ['Female', 'Male'],
                'data': [[0.569620253164557, 0.5897435897435898]],
                'ratio': 0.9658778205833792,
            },
            'group_benefit_equality': {
                'index': ['group_benefit'],
                'columns': ['Female', 'Male'],
                'data': [[0.6455696202531646, 0.717948717948718]],
                'ratio': 0.8991862567811935,
            },
            'disparate_impact': {
                'pairs': [
                    {
                        'reference': ['Female'],
                        'groups': [['Male']],
                        'values': [0.4602076124567474],
                    },
                    {
                        'reference': ['Male'],
                        'groups': [['Female']],
                        'values': [0.4602076124567474],
                    },
                ],
                'absolute_min': {
                    'groups': [['Female'], ['Male']],
                    'value': 0.4602076124567474,
                },
            },
        },
        'model_task': 'BINARY_CLASSIFICATION',
        'total_samples': 1000,
        'valid_samples': 1000,
    },
    'api_version': '3.0',
    'kind': 'NORMAL',
}

FETCH_SLICE_RESPONSE_200 = {
    'data': {
        'metadata': {
            'query': "SELECT * FROM test_bank_churn.bank_churn WHERE geography='France' order by balance desc LIMIT 2",
            'is_slice': True,
            'columns': ['Age'],
            'dtypes': ['int'],
            'model': {
                'id': '36bc3613-49d5-46b5-a0e0-a45c3aa4a9d9',
                'name': 'bank_churn',
            },
            'env': {
                'id': '86e59334-2b86-4726-a970-6900db46e437',
                'type': 'PRE_PRODUCTION',
                'name': 'test_bank_churn',
            },
        },
        'rows': [[57], [37]],
    },
    'api_version': '3.0',
    'kind': 'NORMAL',
}

MUTUAL_INFO_RESPONSE_200 = {
    'data': {
        'CreditScore': 0.009774993816146854,
        'Geography': 1.0387361759590092,
        'Gender': 0.000345600896640319,
        'Age': 0.006747713128151839,
        'Tenure': 0.0017159873190972647,
        'Balance': 0.14278016623398132,
        'NumOfProducts': 0.002155101383831244,
        'HasCrCard': 0.00011152799557884174,
        'IsActiveMember': 0.00026523254634630566,
        'EstimatedSalary': 0.010603971349228138,
        'probability_churned': 0.06073798415644517,
        'Decisions': 2.3682864881247045e-05,
        'Churned': 0.014017045772466472,
    },
    'api_version': '3.0',
    'kind': 'NORMAL',
}

PREDICT_RESPONSE_200 = {
    'data': {'predictions': [{'predicted_quality': 5.759617514660622}]},
    'api_version': '3.0',
    'kind': 'NORMAL',
}

FEATURE_IMPORTANCE_RESPONSE_200 = {
    'data': {
        'loss': 'pointwise_logloss',
        'num_refs': 10000,
        'ci_level': 0.5,
        'mean_loss': 0.35653354054994635,
        'mean_loss_ci': 0.09459192835065221,
        'feature_names': [
            'CreditScore',
            'Geography',
            'Gender',
            'Age',
            'Tenure',
            'Balance',
            'NumOfProducts',
            'HasCrCard',
            'IsActiveMember',
            'EstimatedSalary',
        ],
        'mean_loss_increase_importance': [
            0.004429064308612665,
            0.11303687040447762,
            0.010247568997879158,
            0.20021169408760484,
            0.020512200372182397,
            0.36803439130037513,
            0.2339702870224178,
            0.0014671647143862244,
            0.022758435725508515,
            0.011785520720929346,
        ],
        'random_sample_ci': [
            0.00021145873961269672,
            0.0012444603359610608,
            0.00022339657233601845,
            0.0016025718376113422,
            0.00020151632282746737,
            0.0018154124659677064,
            0.0021341170223544335,
            0.00016283332959968953,
            0.0010258365777659855,
            0.0002324089593535596,
        ],
        'fixed_sample_ci': [
            0.00018964651570488745,
            0.0010810129244220677,
            0.0001612062857999329,
            0.001333218784229577,
            0.000139368878515909,
            0.001191577806041505,
            0.0014415377334894384,
            8.741009867015967e-05,
            0.0007286815550017811,
            0.00019660620632828166,
        ],
        'total_input_samples': 3,
        'valid_input_samples': 3,
        'model_task': 'BINARY_CLASSIFICATION',
        'model_input_type': 'TABULAR',
        'env_id': 'a6385884-4970-4eeb-b8cc-36ce9746cd5e',
        'env_name': DATASET_NAME,
        'created_at': '2023-11-22 16:50:57.705784',
    },
    'api_version': '3.0',
    'kind': 'NORMAL',
}

FEATURE_IMPACT_RESPONSE_200 = {
    'data': {
        'num_inputs': 3,
        'num_refs': 10000,
        'ci_level': 0.5,
        'mean_prediction': 0.08983428988388353,
        'mean_prediction_ci': 0.006687591607821416,
        'feature_names': [
            'CreditScore',
            'Geography',
            'Gender',
            'Age',
            'Tenure',
            'Balance',
            'NumOfProducts',
            'HasCrCard',
            'IsActiveMember',
            'EstimatedSalary',
        ],
        'mean_abs_prediction_change_impact': [
            0.00712590582097325,
            0.04386081743167407,
            0.01618882705936992,
            0.09012170216686392,
            0.003203886657934025,
            0.034259594581994,
            0.03950092221577272,
            0.0008308543417424118,
            0.09500517056814688,
            0.015902298170793795,
        ],
        'random_sample_ci': [
            9.460265530465104e-05,
            0.0004967738708175746,
            0.0001390532937646932,
            0.001011710786484173,
            3.2151564756512305e-05,
            0.0003379320087881252,
            0.0007824117094712736,
            6.632377333582839e-06,
            0.001290117285928614,
            0.0001246149963496527,
        ],
        'fixed_sample_ci': [
            9.387290704313362e-05,
            0.00047072988314235967,
            0.00011810560126585543,
            0.0009869435854980898,
            2.6313946023718767e-05,
            0.0003171540654523467,
            0.0007768114901140053,
            5.596843413373775e-06,
            0.001029967633853864,
            0.00011703590760866858,
        ],
        'model_task': 'BINARY_CLASSIFICATION',
        'model_input_type': 'TABULAR',
        'env_id': 'a6385884-4970-4eeb-b8cc-36ce9746cd5e',
        'env_name': DATASET_NAME,
        'created_at': '2023-11-22 16:50:57.705784',
    },
    'api_version': '3.0',
    'kind': 'NORMAL',
}

PRECOMPUTE_FEATURE_IMPACT_202_RESPONSE = {
    'data': {'job': {'id': JOB_ID, 'name': 'Pre-compute feature impact'}},
    'api_version': '3.0',
    'kind': 'NORMAL',
}
PRECOMPUTE_FEATURE_IMPACT_JOB_API_RESPONSE_200 = {
    'api_version': '3.0',
    'kind': 'NORMAL',
    'data': {
        'name': 'Pre-compute feature impact',
        'id': JOB_ID,
        'info': {
            'resource_type': 'MODEL',
            'resource_name': 'bank_churn',
            'project_name': 'bank_churn',
        },
        'status': 'SUCCESS',
        'progress': 100.0,
        'error_message': None,
        'error_reason': None,
    },
}

PRECOMPUTE_FEATURE_IMPORTANCE_202_RESPONSE = {
    'data': {'job': {'id': JOB_ID, 'name': 'Pre-compute feature importance'}},
    'api_version': '3.0',
    'kind': 'NORMAL',
}
PRECOMPUTE_FEATURE_IMPORTANCE_JOB_API_RESPONSE_200 = {
    'api_version': '3.0',
    'kind': 'NORMAL',
    'data': {
        'name': 'Pre-compute feature importance',
        'id': JOB_ID,
        'info': {
            'resource_type': 'MODEL',
            'resource_name': 'bank_churn',
            'project_name': 'bank_churn',
        },
        'status': 'SUCCESS',
        'progress': 100.0,
        'error_message': None,
        'error_reason': None,
    },
}

PRECOMPUTE_PREDICTIONS_202_RESPONSE = {
    'data': {'job': {'id': JOB_ID, 'name': 'Pre-compute predictions'}},
    'api_version': '3.0',
    'kind': 'NORMAL',
}

PRECOMPUTE_PREDICTIONS_JOB_API_RESPONSE_200 = {
    'api_version': '3.0',
    'kind': 'NORMAL',
    'data': {
        'name': 'Pre-compute predictions',
        'id': JOB_ID,
        'info': {
            'resource_type': 'MODEL',
            'resource_name': 'bank_churn',
            'project_name': 'bank_churn',
        },
        'status': 'SUCCESS',
        'progress': 100.0,
        'error_message': None,
        'error_reason': None,
    },
}


@responses.activate
def test_explain() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/explain',
        json=EXPLAIN_RESPONSE_200,
    )
    explain_result = model.explain(
        input_data_source=RowDataSource(
            row={
                'CreditScore': 619,
                'Geography': 'France',
                'Gender': 'Female',
                'Age': 42,
                'Tenure': 2,
                'Balance': 0.0,
                'NumOfProducts': 1,
                'HasCrCard': 'Yes',
                'IsActiveMember': 'Yes',
                'EstimatedSalary': 101348.88,
            },
        ),
        ref_data_source=DatasetDataSource(
            env_type='PRODUCTION',
        ),
    )
    assert explain_result == namedtuple('Explain', EXPLAIN_RESPONSE_200['data'])(
        **EXPLAIN_RESPONSE_200['data']
    )


@responses.activate
def test_fairness() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/fairness',
        json=FAIRNESS_RESPONSE_200,
    )
    fairness = model.get_fairness(
        data_source=DatasetDataSource(
            env_type='PRODUCTION',
        ),
        protected_features=['Gender'],
        positive_outcome='Churned',
    )
    assert fairness == namedtuple('Fairness', FAIRNESS_RESPONSE_200['data'])(
        **FAIRNESS_RESPONSE_200['data']
    )


@responses.activate
def test_get_slice() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/slice-query/fetch',
        json=FETCH_SLICE_RESPONSE_200,
    )

    slice_df = model.get_slice(
        query="SELECT * FROM test_bank_churn.bank_churn WHERE geography='France' order by balance desc LIMIT 3",
        columns=['Age'],
        max_rows=2,
    )
    expected_df = pd.DataFrame({'Age': [57, 37]})
    pd.testing.assert_frame_equal(expected_df, slice_df)


@responses.activate
def test_slice_download() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    parquet_path = os.path.join(OUTPUT_DIR, 'test_slice_download.parquet')
    parquet_output = os.path.join(BASE_TEST_DIR, 'slice_test_dir')
    with open(parquet_path, 'rb') as parquet_file:
        data = io.BufferedReader(parquet_file)
        responses.post(
            url=f'{URL}/v3/slice-query/download',
            body=data,
        )
        expected_df = pd.DataFrame({'Age': [38, 57, 42]})
        model.download_slice(
            output_dir=parquet_output,
            query='SELECT * FROM test_bank_churn.bank_churn WHERE age>=20 order by balance desc',
            columns=['Age'],
            max_rows=3,
        )
        slice_df = pd.read_parquet(parquet_path)
        pd.testing.assert_frame_equal(expected_df, slice_df)
    shutil.rmtree(str(parquet_output))


@responses.activate
def test_mutual_info() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/mutual-info',
        json=MUTUAL_INFO_RESPONSE_200,
    )
    mutual_info = model.get_mutual_info(
        query=f'select * from {DATASET_NAME}.{MODEL_NAME}',
        column_name='Geography',
    )
    assert mutual_info == MUTUAL_INFO_RESPONSE_200['data']


@responses.activate
def test_predict() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/predict',
        json=PREDICT_RESPONSE_200,
    )
    data = {
        'row_id': 1109,
        'fixed acidity': 10.8,
        'volatile acidity': 0.47,
        'citric acid': 0.43,
        'residual sugar': 2.1,
        'chlorides': 0.171,
        'free sulfur dioxide': 27.0,
        'total sulfur dioxide': 66.0,
        'density': 0.9982,
        'pH': 3.17,
        'sulphates': 0.76,
        'alcohol': 10.8,
    }
    df = pd.DataFrame(data, index=data.keys())
    predictions = model.predict(df=df)

    expected_result = pd.DataFrame(PREDICT_RESPONSE_200['data']['predictions'])
    pd.testing.assert_frame_equal(predictions, expected_result)


@responses.activate
def test_get_feature_impact() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/feature-impact',
        json=FEATURE_IMPACT_RESPONSE_200,
    )
    feature_impact = model.get_feature_impact(
        data_source=DatasetDataSource(
            env_type='PRE-PRODUCTION',
            env_id=DATASET_ID,
        ),
    )

    assert feature_impact == namedtuple(
        'FeatureImpact', FEATURE_IMPACT_RESPONSE_200['data']
    )(**FEATURE_IMPACT_RESPONSE_200['data'])


@responses.activate
def test_get_feature_importance() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/feature-importance',
        json=FEATURE_IMPORTANCE_RESPONSE_200,
    )
    feature_importance = model.get_feature_importance(
        data_source=DatasetDataSource(
            env_type='PRE-PRODUCTION',
            env_id=DATASET_ID,
        ),
    )

    assert feature_importance == namedtuple(
        'FeatureImportance', FEATURE_IMPORTANCE_RESPONSE_200['data']
    )(**FEATURE_IMPORTANCE_RESPONSE_200['data'])


@responses.activate
def test_precompute_feature_impact() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/precompute-feature-impact',
        json=PRECOMPUTE_FEATURE_IMPACT_202_RESPONSE,
    )
    responses.get(
        url=f'{URL}/v3/jobs/{JOB_ID}',
        json=PRECOMPUTE_FEATURE_IMPACT_JOB_API_RESPONSE_200,
    )

    job_obj = model.precompute_feature_impact(dataset_id=DATASET_ID, update=False)
    assert isinstance(job_obj, Job)


@responses.activate
def test_update_precompute_feature_impact() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.put(
        url=f'{URL}/v3/analytics/precompute-feature-impact',
        json=PRECOMPUTE_FEATURE_IMPACT_202_RESPONSE,
    )
    responses.get(
        url=f'{URL}/v3/jobs/{JOB_ID}',
        json=PRECOMPUTE_FEATURE_IMPACT_JOB_API_RESPONSE_200,
    )

    job_obj = model.precompute_feature_impact(dataset_id=DATASET_ID, update=True)
    assert isinstance(job_obj, Job)


@responses.activate
def test_precompute_feature_importance() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/precompute-feature-importance',
        json=PRECOMPUTE_FEATURE_IMPORTANCE_202_RESPONSE,
    )
    responses.get(
        url=f'{URL}/v3/jobs/{JOB_ID}',
        json=PRECOMPUTE_FEATURE_IMPORTANCE_JOB_API_RESPONSE_200,
    )

    job_obj = model.precompute_feature_importance(dataset_id=DATASET_ID, update=False)
    assert isinstance(job_obj, Job)


@responses.activate
def test_update_precompute_feature_importance() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.put(
        url=f'{URL}/v3/analytics/precompute-feature-importance',
        json=PRECOMPUTE_FEATURE_IMPORTANCE_202_RESPONSE,
    )
    responses.get(
        url=f'{URL}/v3/jobs/{JOB_ID}',
        json=PRECOMPUTE_FEATURE_IMPORTANCE_JOB_API_RESPONSE_200,
    )

    job_obj = model.precompute_feature_importance(dataset_id=DATASET_ID, update=True)
    assert isinstance(job_obj, Job)


@responses.activate
def test_get_precomputed_feature_importance() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/feature-importance/precomputed',
        json=FEATURE_IMPORTANCE_RESPONSE_200,
    )
    assert model.get_precomputed_feature_importance() == namedtuple(
        'FeatureImportance', FEATURE_IMPORTANCE_RESPONSE_200['data']
    )(**FEATURE_IMPORTANCE_RESPONSE_200['data'])


@responses.activate
def test_get_precomputed_feature_impact() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/feature-impact/precomputed',
        json=FEATURE_IMPACT_RESPONSE_200,
    )
    assert model.get_precomputed_feature_impact() == namedtuple(
        'FeatureImpact', FEATURE_IMPACT_RESPONSE_200['data']
    )(**FEATURE_IMPACT_RESPONSE_200['data'])


@responses.activate
def test_precompute_predictions() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.post(
        url=f'{URL}/v3/analytics/precompute-predictions',
        json=PRECOMPUTE_PREDICTIONS_202_RESPONSE,
    )
    responses.get(
        url=f'{URL}/v3/jobs/{JOB_ID}',
        json=PRECOMPUTE_PREDICTIONS_JOB_API_RESPONSE_200,
    )

    job_obj = model.precompute_predictions(dataset_id=DATASET_ID, update=False)
    assert isinstance(job_obj, Job)


@responses.activate
def test_update_precompute_predictions() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    model = Model.get(id_=MODEL_ID)

    responses.put(
        url=f'{URL}/v3/analytics/precompute-predictions',
        json=PRECOMPUTE_PREDICTIONS_202_RESPONSE,
    )
    responses.get(
        url=f'{URL}/v3/jobs/{JOB_ID}',
        json=PRECOMPUTE_PREDICTIONS_JOB_API_RESPONSE_200,
    )

    job_obj = model.precompute_predictions(dataset_id=DATASET_ID, update=True)
    assert isinstance(job_obj, Job)
