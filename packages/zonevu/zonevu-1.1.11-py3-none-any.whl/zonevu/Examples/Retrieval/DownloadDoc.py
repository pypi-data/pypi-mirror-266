from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from azure.storage.blob import BlobServiceClient
from pathlib import Path


def main(zonevu: Zonevu, well_name: str) -> None:
    print('Retrieve a well and one of its documents')
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    if len(well.documents) > 0:
        doc = well.documents[0]
        doc_service = zonevu.document_service
        cred = doc_service.get_doc_download_credential(doc)
        blob_svc = BlobServiceClient(account_url=cred.url, credential=cred.token)
        client = blob_svc.get_blob_client(container=cred.container, blob=cred.path)
        blob_exists = client.exists()

        if blob_exists:
            cloud_path = Path(cred.path)
            path = Path('c:/delme') / (cloud_path.stem + '2' + cloud_path.suffix)
            with open(file=path, mode="wb") as local_file:
                download_stream = client.download_blob()
                local_file.write(download_stream.readall())

    print('Completed')




