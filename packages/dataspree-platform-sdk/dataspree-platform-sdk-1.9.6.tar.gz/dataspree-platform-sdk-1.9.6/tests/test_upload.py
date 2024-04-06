import time
from datetime import datetime
import os
import pytest
import logging
logger = logging.getLogger(__name__)

from dataspree.platform_sdk.client import Client


@pytest.fixture
def sdk_client() -> Client:
    username = os.getenv('DS_USERNAME')
    password = os.getenv('DS_PASSWORD')
    server_url = os.getenv('DS_SERVER_URL')

    # check connection
    client = Client(username, password, server_url=server_url)
    server_status = client.server_status()
    assert server_status is not None

    logger.info(f'Testing with Data Spree AI Platform Version {server_status["version"]}')

    return client


@pytest.mark.integration_test
def test_upload_inference_results(sdk_client: Client):
    test_start = datetime.utcnow()

    # create class label
    class_label = sdk_client.create_class_label(f'Integration Test Class Label {test_start}', False)
    assert class_label is not None

    class_label_id = class_label['id']

    # create a test dataset
    dataset_id = sdk_client.create_dataset(f'Integration Test Dataset {test_start.isoformat()}',
                                            classification_class_label_ids=[class_label_id])
    assert dataset_id is not None and dataset_id != -1

    # upload exemplary items
    image_file = b'test'

    items = [sdk_client.create_dataset_item(image_file=image_file,
                                             image_file_name='test.dat',
                                             dataset_id=dataset_id,
                                             annotations={}) for _ in range(5)]
    # all items must have IDs
    for i in items:
        assert i is not None and i != -1

    # create train and test subset
    train_subset = sdk_client.create_data_subset('train', dataset_id)
    assert train_subset is not None

    test_subset = sdk_client.create_data_subset('test', dataset_id)
    assert test_subset is not None

    # add items to subsets
    sdk_client.add_dataset_items_to_subset(items[:2], train_subset)
    sdk_client.add_dataset_items_to_subset(items[2:], test_subset)

    # create test model
    model_data = {
        'name': f'Integration Test Model {test_start}',
        'class_label_ids': [class_label_id],
        'data_subsets': [
            {'category': 'classification_train', 'data_subset': train_subset['id']},
            {'category': 'classification_test', 'data_subset': test_subset['id']}
        ],
        'network_config_option': 1,
        'network_type': 'classification',
        'parameters': {}
    }

    response = sdk_client.http.post(f'{sdk_client.server_url}/models/', data=model_data)
    response.raise_for_status()
    model = response.json()

    # upload inference results
    results = dict()
    now = int(time.time() * 1000)
    iteration = 1000

    sdk_client.upload_inference_results(results, now, iteration, model['id'])
