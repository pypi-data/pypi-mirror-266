from langchain_community.document_loaders import S3FileLoader

from komodo.framework.komodo_datasource import KomodoDataSource
from komodo.shared.documents.text_extract import to_clean_text


class S3BucketKey(KomodoDataSource):
    def __init__(self, name, bucket, key):
        super().__init__(name, type="s3bucketkey")
        self.bucket = bucket
        self.key = key

    def list_items(self):
        import boto3
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=self.bucket, Prefix=self.key)
        return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('/') is False]

    def list_items_with_details(self):
        import boto3
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=self.bucket, Prefix=self.key)
        return response.get('Contents', [])

    def get_item(self, key):
        documents = S3FileLoader(self.bucket, key).load()
        for d in documents:
            d.page_content = to_clean_text(d.page_content)
        return documents
