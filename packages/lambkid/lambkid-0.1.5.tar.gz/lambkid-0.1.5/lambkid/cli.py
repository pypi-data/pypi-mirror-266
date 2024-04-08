import fire
from lambkid.libs.minio_client import MinIO

class minio():
    def upload_file(self,minio_url,access_key,secret_key,bucket_name,object_name,file_path,content_type="text/plain;charset=utf-8"):
        """
        upload file to minio server
        :param minio_url:  url of minio server
        :param access_key:  access key
        :param secret_key:  secret key
        :param bucket_name:  bucket name
        :param object_name:  object name
        :param file_path:  file path to upload
        :param content_type:  content typek, default text/plain;charset=utf-8
        :return:
        """
        return MinIO().upload_file(minio_url,access_key,secret_key,bucket_name,object_name,file_path,content_type)


if __name__=="__main__":
    fire.Fire(
        {
            "minio": minio
        }
    )