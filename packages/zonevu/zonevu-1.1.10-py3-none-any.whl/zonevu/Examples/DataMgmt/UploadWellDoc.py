from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from pathlib import Path
from ...DataModels.Document import Document, DisciplineTypeEnum


def main(zonevu: Zonevu, well_name: str, local_file_path: Path) -> None:
    # Deleting wells requires a delete code
    well_svc = zonevu.well_service

    # Find a well by name
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find a well with name "%s"' % well_name)

    if not local_file_path.exists():
        raise ZonevuError.local('Could not find a with name "%s"' % local_file_path)

    # Create document catalog entry and set a few fields
    file_name = local_file_path.name
    file_size = local_file_path.stat().st_size
    server_file_path = Path('Documents/Photos/%s' % file_name)   # Server file path must start with 'Documents'
    doc = well.create_doc(server_file_path, file_size)
    doc.author = zonevu.company.UserName
    doc.discipline = DisciplineTypeEnum.Drilling

    doc_svc = zonevu.document_service
    doc_svc.create_document(doc)            # Create document entry in zonevu document index
    doc_svc.upload_doc(doc, local_file_path)      # Upload the actual document

