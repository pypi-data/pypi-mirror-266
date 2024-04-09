# 引入Minio包。
import json

from botocore.exceptions import ClientError
import logging

class OSSServiceFactory:
    @staticmethod
    def creatStorageProvider(provider:str,cateogry:str,settings:dict):
        if cateogry == 's3' or cateogry == 'aws':
            return AWSS3Service(provider,settings)
        elif cateogry == 'minio':
            return MinoService(provider,settings)
        else:
            raise Exception("Unkonw CloudFileService")


class CloudFileService:

    def __init__(self,provider:str,settings:dict):
        self.setttings=settings
        self.provider=provider
        self.client=None

    def upload(self,bucket:str,src_path:str,dst_path:str,metadata:dict):
        #raise Exception("Can not call the abstract method")
        return {"bucket":bucket,"key":dst_path,"provider":self.provider}



class AWSS3Service(CloudFileService):
    """
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """
    def __init__(self,provider:str,settings:dict):
        super().__init__(provider,settings)
        self.endpoint = settings['endpoint']
        self.access_key = settings['access_key']
        self.secret_key = settings['secret_key']
        self.secure = settings['secure']
        self.bucket=settings['bucket']
        self.client=None

    def __connect__(self):
        import boto3
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint,
                verify=False
            )

        except ClientError as err:
            raise err

    def upload(self,bucket:str,src_path:str,dst_path:str,metadata:dict):
        self.__connect__()
        try:

            content_type = "application/octet-stream" if "content-type" not in metadata.keys() else metadata['content-type']
            response = self.client.put_object(Bucket=bucket, Body=open(src_path, 'rb'),
                                              Key=dst_path,
                ContentType=content_type,
                Metadata=metadata)
            """
            {'ResponseMetadata': {'RequestId': 'FEASEX6M9V2V2E5Q', 'HostId': 'FsSozf3bTabOIrmNIvZnnwRjbDpy/uKKTqnyWMLWVpg3uOpor+3TJvQqWIxkSzrMv5gBWPvEiadW45tKzt2OcA==', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': 'FsSozf3bTabOIrmNIvZnnwRjbDpy/uKKTqnyWMLWVpg3uOpor+3TJvQqWIxkSzrMv5gBWPvEiadW45tKzt2OcA==', 'x-amz-request-id': 'FEASEX6M9V2V2E5Q', 'date': 'Sun, 19 Mar 2023 15:32:00 GMT', 'x-amz-server-side-encryption': 'AES256', 'etag': '"8983b25e38ccb97b45921d966f0998d8"', 'server': 'AmazonS3', 'content-length': '0'}, 'RetryAttempts': 1}, 'ETag': '"8983b25e38ccb97b45921d966f0998d8"', 'ServerSideEncryption': 'AES256'}
            """
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {"result":{"etag":response['ETag'],"bucket":bucket,"key":dst_path,"provider":self.provider},"status":200}
            else:

                # return {"result": "error", "status": response['ResponseMetadata']['HTTPStatusCode'], "error": json.dump(response)}
                raise Exception("Upload file to s3 failed: {}".format(json.dumps(response)))
        except Exception as e:
            logging.error(e)

            return {"result":"error","status":500,"error":str(e)}





class MinoService(CloudFileService):
    def __init__(self, provider:str,settings: dict):
        super().__init__(provider,settings)
        self.endpoint = settings['endpoint']
        self.access_key = settings['access_key']
        self.secret_key = settings['secret_key']
        self.secure = settings['secure']
        self.bucket=settings['bucket']
        self.client = None


    def __connect__(self):

        from minio import Minio
        if self.client is None:
            try:
                self.client = Minio(self.endpoint,
                                    access_key=self.access_key,
                                    secret_key=self.secret_key,
                                    secure=False)

            except Exception as err:
                raise err

    def upload(self,bucket:str,src_path:str,dst_path:str,metadata:dict):
        self.__connect__()
        import os
        try:
            with open(src_path, 'rb') as file_data:
                file_stat = os.stat(src_path)
                rsp=self.client.put_object(
                    bucket,
                    dst_path,
                    file_data,
                    file_stat.st_size,
                    metadata=metadata
                )
                return {"result":{"etag":rsp.etag,"bucket":rsp.bucket_name,"key":rsp.object_name,"provider":self.provider},"status":200}

        except ClientError as e:
            logging.error(e)
            return {"result": "error", "status": 500,"error": str(e)}


if __name__ == '__main__':

    metadata={"filename":"a.json","content-type":"application/json","content-type": "application/octet-stream"}
    src_file= "/inhand-product-ci.sample"
    key="2023-03-19/{}".format(src_file[src_file.rindex("/")+1:])


    minio_settings={"access_key":"protected-user","secret_key":"rnk4gVRMxojVXkv","endpoint":"files.inhand.design","secure":False}
    minio_svc=OSSServiceFactory.creatStorageProvider("cn.product.protected.resources.","minio",minio_settings)
    rsp=minio_svc.upload("protected-files",src_file,key,metadata)
    print("response: {}".format(rsp))


    s3_settings={"access_key":"AKIAYFRJLY5HJZKFTKAN",
                 "secret_key":"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",
                 "endpoint":"https://s3.cn-north-1.amazonaws.com.cn",
                 "region":"cn-north-1",
                 "secure":False}
    s3_svc=OSSServiceFactory.creatStorageProvider("cn.product.protected.resources","s3",s3_settings)

    rsp=s3_svc.upload("internet-protected-files",src_file,key,metadata)
    print("response: {}".format(rsp))







