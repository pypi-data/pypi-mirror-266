import json
import numpy as np

from .tools import current_time_ms, non_empty_list, flatten
from .storage._s3_client import _load_from_bucket, _upload_to_bucket
from .storage._sns_client import _get_sns_client

PROGRESS_EXT = '.progress'


# fix error "Object of type int64 is not JSON serializable"
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def upload_json(bucket_name: str, file_key: str, body: dict):
    return _upload_to_bucket(
        bucket=bucket_name,
        key=file_key,
        body=json.dumps(body, indent=2, ensure_ascii=False, cls=NpEncoder).encode('utf8'),
        content_type='application/json'
    )


def _to_file_progress(filepath: str):
    return filepath.replace('.csv', PROGRESS_EXT).replace('.json', PROGRESS_EXT).replace('.hestia', PROGRESS_EXT)


def handle_result(bucket_name: str, file_key: str, step: str, start: int, content: dict):
    filepath = _to_file_progress(file_key)

    # try to read existing progress to update the time per step
    try:
        data = json.loads(_load_from_bucket(bucket_name, filepath))
    except Exception:
        data = {}

    return upload_json(bucket_name, filepath, {
        'step': step,
        'time': {
            **(data.get('time', {}) if isinstance(data.get('time', {}), dict) else {}),
            step: current_time_ms() - start
        },
        **content
    })


def handle_error(
    bucket_name: str, file_key: str, step: str, start: int,
    err: str = '', stack: str = '', errors=[], warnings=[],
    extras: dict = {}
):
    return handle_result(bucket_name, file_key, step, start, extras | {
        'success': False,
        'error': {
            'message': err,
            'stack': stack,
            'errors': errors,
            'warnings': warnings
        },
        'warning': {
            'warnings': warnings
        }
    })


def handle_success(bucket_name: str, file_key: str, step: str, start: int, extras: dict = {}):
    return handle_result(bucket_name, file_key, step, start, extras | {'success': True})


def publish_result(topic_arn: str, bucket_name: str, file_key: str, filepath: str, step: str, success: bool):
    return _get_sns_client().publish(
        TopicArn=topic_arn,
        Message=json.dumps({
            'bucket': bucket_name,
            'key': file_key,
            'filepath': filepath
        }, indent=2),
        MessageAttributes={
            'functionName': {
                'DataType': 'String',
                'StringValue': step + ('Done' if success else 'Error')
            }
        }
    )


def _parse_event_s3(event: dict): return {'bucket': event['s3']['bucket']['name'], 'key': event['s3']['object']['key']}


def _parse_event_SNS(event: dict):
    event = event.get('Sns', {})
    data = json.loads(event.get('Message', '{}'))
    attributes: dict = event.get('MessageAttributes', {})
    data['attributes'] = {key: value.get('Value') for key, value in attributes.items()}
    return data


def _parse_event_SQS(event: dict):
    condition = event.get('requestContext', {}).get('condition')
    return _get_data_from_event(event.get('requestPayload', {})) if condition != 'RetriesExhausted' else None


def _get_data_from_event(event):  # noqa: C901
    if isinstance(event, dict):
        if 's3' in event:
            return _parse_event_s3(event)
        # invoked when running asynchronously
        if 'Sns' in event:
            return _parse_event_SNS(event)
        # invoked through http event
        if 'body' in event:
            return _get_data_from_event(json.loads(event.get('body', '{}')))
        # invoked through s3 put object
        if 'Records' in event:
            return flatten(map(_get_data_from_event, event.get('Records', [])))
        # invoked when calculation timedout or failed
        if 'requestPayload' in event:
            return _parse_event_SQS(event)
        return event
    if isinstance(event, str):
        return _get_data_from_event(json.loads(event))


def parse_event(event: dict):
    data = _get_data_from_event(event)
    return non_empty_list(flatten(data) if isinstance(data, list) else [data])
