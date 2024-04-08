import fire
from lambkid.libs.minio_client import MinIO


def main():
    fire.Fire(
        {
            "minio":MinIO
        }
    )

if __name__=="__main__":
    main()