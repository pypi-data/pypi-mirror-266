import json
import logging
from http import HTTPStatus
from uuid import UUID

import pytest
import responses

from fiddler.constants.alert_rule import AlertCondition, BinSize, CompareTo, Priority
from fiddler.entities.alert_rule import AlertRule
from fiddler.exceptions import NotFound
from fiddler.schemas.alert_rule import NotificationConfig
from fiddler.tests.apis.test_baseline import (
    API_RESPONSE_200 as BASELINE_API_RESPONSE_200,
)
from fiddler.tests.apis.test_model import API_RESPONSE_200 as MODEL_API_RESPONSE_200
from fiddler.tests.constants import (
    ALERT_RULE_ID,
    BASELINE_ID,
    BASELINE_NAME,
    MODEL_ID,
    MODEL_NAME,
    PROJECT_ID,
    PROJECT_NAME,
    URL,
)
from fiddler.utils.logger import set_logging

API_RESPONSE_200 = {
    'data': {
        'feature_names': ['age'],
        'id': 620,
        'created_at': '2023-11-28T08:04:12.651937+00:00',
        'organization_name': 'mainbuild',
        'compare_period': None,
        'time_bucket': 3600000,
        'alert_type': 'data_integrity',
        'metric_display_name': 'Missing Value Violation',
        'enable_notification': True,
        'last_updated': '2023-11-28T08:04:12.653346+00:00',
        'alert_type_display_name': 'Data Integrity',
        'critical_threshold': 0.0,
        'baseline_name': BASELINE_NAME,
        'baseline': {
            'id': BASELINE_ID,
            'name': BASELINE_NAME,
        },
        'condition': 'greater',
        'uuid': ALERT_RULE_ID,
        'segment': None,
        'warning_threshold': None,
        'name': 'Age Missing 1 Hr',
        'model_name': MODEL_NAME,
        'model': {
            'id': MODEL_ID,
            'name': MODEL_NAME,
        },
        'is_active': True,
        'created_by': 'admin@fiddler.ai',
        'bin_size': 'Hour',
        'category': None,
        'project_name': PROJECT_NAME,
        'project': {
            'id': PROJECT_ID,
            'name': PROJECT_NAME,
        },
        'metric': 'null_violation_count',
        'metric_id': 'null_violation_count',
        'compare_to': 'raw_value',
        'priority': 'HIGH',
        'notifications': {
            'emails': {'alert_config_uuid': ALERT_RULE_ID, 'email': 'admin@fiddler.ai'},
            'pagerduty': {
                'severity': '',
                'alert_config_uuid': ALERT_RULE_ID,
                'service': '',
            },
            'webhooks': [{'uuid': 'e20bf4cc-d2cf-4540-baef-d96913b14f1b'}],
        },
    },
    'api_version': '2.0',
    'kind': 'NORMAL',
}

API_RESPONSE_404 = {
    'error': {
        'code': 404,
        'message': "AlertConfig({'uuid': 'ff9a897b-be5b-48e6-909f-13073a6d0fe8'}) not found",
        'errors': [
            {
                'reason': 'ObjectNotFound',
                'message': "AlertConfig({'uuid': 'ff9a897b-be5b-48e6-909f-13073a6d0fe8'}) not found",
                'help': '',
            }
        ],
    },
    'api_version': '2.0',
    'kind': 'ERROR',
}

LIST_API_RESPONSE = {
    'data': {
        'page_size': 100,
        'total': 2,
        'item_count': 2,
        'page_count': 1,
        'page_index': 1,
        'offset': 0,
        'items': [
            API_RESPONSE_200['data'],
            {
                'critical_threshold': 100.0,
                'created_by': 'admin@fiddler.ai',
                'metric_display_name': 'Traffic',
                'condition': 'lesser',
                'metric': 'traffic',
                'metric_id': 'traffic',
                'bin_size': 'Hour',
                'enable_notification': True,
                'is_active': True,
                'project_name': PROJECT_NAME,
                'project': {
                    'id': PROJECT_ID,
                    'name': PROJECT_NAME,
                },
                'name': 'traffic-lt-1hr',
                'created_at': '2023-11-28T08:04:10.916498+00:00',
                'baseline_name': 'DEFAULT (bank_churn)',
                'baseline': {
                    'id': BASELINE_ID,
                    'name': BASELINE_NAME,
                },
                'organization_name': 'mainbuild',
                'priority': 'HIGH',
                'category': None,
                'warning_threshold': 200.0,
                'segment': None,
                'alert_type': 'service_metrics',
                'time_bucket': 3600000,
                'alert_type_display_name': 'Traffic',
                'compare_period': 5,
                'compare_to': 'time_period',
                'uuid': '42eb6d51-dc5c-4e04-82aa-440b2d840704',
                'id': 618,
                'feature_names': None,
                'model_name': MODEL_NAME,
                'model': {
                    'id': MODEL_ID,
                    'name': MODEL_NAME,
                },
                'last_updated': '2023-11-28T08:04:10.918587+00:00',
            },
        ],
    }
}

LIST_API_RESPONSE_EMPTY = {
    'data': {
        'page_size': 100,
        'total': 2,
        'item_count': 2,
        'page_count': 1,
        'page_index': 1,
        'offset': 0,
        'items': [],
    }
}


@responses.activate
def test_get_alert_rule_success() -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )

    alert_rule = AlertRule.get(id_=ALERT_RULE_ID)

    assert isinstance(alert_rule, AlertRule)


@responses.activate
def test_get_alert_rule_not_found() -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_404,
        status=HTTPStatus.NOT_FOUND,
    )

    with pytest.raises(NotFound):
        AlertRule.get(id_=ALERT_RULE_ID)


@responses.activate
def test_alert_rule_list_success() -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs',
        json=LIST_API_RESPONSE,
    )
    for rule in AlertRule.list(model_id=MODEL_ID):
        assert isinstance(rule, AlertRule)


@responses.activate
def test_alert_rule_list_empty() -> None:

    responses.get(
        url=f'{URL}/v2/alert-configs',
        json=LIST_API_RESPONSE_EMPTY,
    )

    assert len(list(AlertRule.list(model_id=MODEL_ID))) == 0


@responses.activate
def test_delete_alert_rule() -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )
    rule = AlertRule.get(id_=ALERT_RULE_ID)

    responses.delete(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
    )

    rule.delete()


@responses.activate
def test_delete_alert_rule_not_found() -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )
    rule = AlertRule.get(id_=ALERT_RULE_ID)

    responses.delete(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_404,
        status=HTTPStatus.NOT_FOUND,
    )

    with pytest.raises(NotFound):
        rule.delete()


@responses.activate
def test_add_alert_rule_success() -> None:
    responses.get(
        url=f'{URL}/v3/models/{MODEL_ID}',
        json=MODEL_API_RESPONSE_200,
    )
    responses.get(
        url=f'{URL}/v3/baselines/{BASELINE_ID}',
        json=BASELINE_API_RESPONSE_200,
    )
    responses.post(
        url=f'{URL}/v2/alert-configs',
        json=API_RESPONSE_200,
    )
    alert_rule = AlertRule(
        name='alert_name',
        model_id=MODEL_ID,
        metric_id='drift',
        priority=Priority.HIGH,
        compare_to=CompareTo.RAW_VALUE,
        condition=AlertCondition.GREATER,
        bin_size=BinSize.HOUR,
        critical_threshold=0.5,
        warning_threshold=0.1,
        columns=['gender', 'creditscore'],
    ).create()

    assert isinstance(alert_rule, AlertRule)
    assert alert_rule.id == UUID(ALERT_RULE_ID)
    assert alert_rule.model.id == UUID(MODEL_ID)
    assert alert_rule.project_id == UUID(PROJECT_ID)


@responses.activate
def test_enable_notifications(caplog) -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )

    alert_rule = AlertRule.get(id_=ALERT_RULE_ID)

    resp = responses.patch(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )
    set_logging(logging.INFO)

    alert_rule.enable_notifications()
    assert json.loads(resp.calls[0].request.body) == {'enable_notification': True}
    assert (
        f'Notifications have been enabled for alert rule with id: {ALERT_RULE_ID}'
        == caplog.messages[0]
    )


@responses.activate
def test_disable_notifications(caplog) -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )

    alert_rule = AlertRule.get(id_=ALERT_RULE_ID)

    API_RESPONSE_200['enable_notification'] = False

    resp = responses.patch(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )

    set_logging(logging.INFO)
    alert_rule.disable_notifications()
    assert json.loads(resp.calls[0].request.body) == {'enable_notification': False}
    assert (
        f'Notifications have been disabled for alert rule with id: {ALERT_RULE_ID}'
        == caplog.messages[0]
    )


@responses.activate
def test_set_notifications() -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )

    alert_rule = AlertRule.get(id_=ALERT_RULE_ID)
    API_RESPONSE_200['data']['notifications'] = {
        'webhooks': [
            {'uuid': 'e20bf4cc-d2cf-4540-baef-d96913b14f1b'},
            {'uuid': '6e796fda-0111-4a72-82cd-f0f219e903e1'},
        ],
        'emails': {
            'alert_config_uuid': ALERT_RULE_ID,
            'email': 'nikhil@fiddler.ai, admin@fiddler.ai',
        },
        'pagerduty': {
            'service': '',
            'alert_config_uuid': ALERT_RULE_ID,
            'severity': '',
        },
    }
    responses.patch(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )
    notifications = alert_rule.set_notification_config(
        emails=['nikhil@fiddler.ai', 'admin@fiddler.ai'],
        webhooks=[
            'e20bf4cc-d2cf-4540-baef-d96913b14f1b',
            '6e796fda-0111-4a72-82cd-f0f219e903e1',
        ],
    )
    assert notifications == NotificationConfig(
        **{
            'emails': ['nikhil@fiddler.ai', 'admin@fiddler.ai'],
            'webhooks': [
                'e20bf4cc-d2cf-4540-baef-d96913b14f1b',
                '6e796fda-0111-4a72-82cd-f0f219e903e1',
            ],
        }
    )


@responses.activate
def test_get_notifications() -> None:
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )

    alert_rule = AlertRule.get(id_=ALERT_RULE_ID)
    responses.get(
        url=f'{URL}/v2/alert-configs/{ALERT_RULE_ID}',
        json=API_RESPONSE_200,
    )
    notifications = alert_rule.get_notification_config()
    assert notifications == NotificationConfig(
        **{
            'emails': ['nikhil@fiddler.ai', 'admin@fiddler.ai'],
            'webhooks': [
                'e20bf4cc-d2cf-4540-baef-d96913b14f1b',
                '6e796fda-0111-4a72-82cd-f0f219e903e1',
            ],
        }
    )
