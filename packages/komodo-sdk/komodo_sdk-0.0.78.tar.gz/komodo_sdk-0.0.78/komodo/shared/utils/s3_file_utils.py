import boto3

KOMODO_BUCKET = 'incoming.kmdo.app'

INBOX_PREFIX = 'test'
EXPLODED_PREFIX = 'exploded'
TEXTRACT_PREFIX = 'extracted'
VECSTORE_PREFIX = 'vecstore'
RESPONSE_PREFIX = 'responses'

OUTPUT_HTML_TEMPLATE = "processed_template.txt"


def read_s3_file(key):
    client = boto3.client('s3')
    mail_content = client.get_object(Bucket=KOMODO_BUCKET, Key=key)
    body = mail_content['Body']
    return body.read()


def write_s3_file(key, body, content_type):
    client = boto3.client('s3')
    client.put_object(Bucket=KOMODO_BUCKET, Key=key, Body=body, ContentType=content_type)


def read_message(message_id):
    key = INBOX_PREFIX + "/" + message_id
    return read_s3_file(key).decode('utf-8')


def response_key(assistant, message_id, run_id):
    return RESPONSE_PREFIX + "/" + assistant['name'] + "/" + message_id + "/" + run_id


def read_response_html(assistant, message_id, run_id):
    key = response_key(assistant, message_id, run_id) + "/" + OUTPUT_HTML_TEMPLATE
    return read_s3_file(key).decode('utf-8')


def list_attachments(message_id):
    key = TEXTRACT_PREFIX + "/" + message_id
    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=KOMODO_BUCKET, Prefix=key)
    return response['Contents'] if 'Contents' in response else []


def list_attachments_keys(message_id):
    return [x['Key'] for x in list_attachments(message_id)]


def list_attachments_keys_no_parts(message_id):
    all_keys = [x['Key'] for x in list_attachments(message_id)]
    real_keys = filter(lambda x: not x.split('/')[-1].startswith("part"), all_keys)
    return list(real_keys)


def list_attachments_names(message_id):
    return [x.split("/")[-1] for x in list_attachments_keys(message_id)]


def list_vector_store_objects(message_id):
    key = VECSTORE_PREFIX + "/" + message_id
    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=KOMODO_BUCKET, Prefix=key)
    return response['Contents']


def list_vector_store_keys(message_id):
    return [x['Key'] for x in list_vector_store_objects(message_id)]


def s3_url_for(prefix, bucket=KOMODO_BUCKET):
    return "https://s3.console.aws.amazon.com/s3/object/" + bucket + "?region=us-east-1" + "&prefix=" + prefix


def save_to_s3(key, body, content_type):
    write_s3_file(key, body, content_type)
    return s3_url_for(key)


class BaseExporter():
    def write(self, name, body, content_type):
        print(name, body, content_type)


class NoopExporter():
    def write(self, name, body, content_type):
        print(name, body, content_type)


class S3Exporter(BaseExporter):
    def __init__(self, prefix, bucket=KOMODO_BUCKET):
        self.base = prefix

    def write(self, name, body, content_type):
        key = self.base + "/" + name
        write_s3_file(key, body, content_type)
