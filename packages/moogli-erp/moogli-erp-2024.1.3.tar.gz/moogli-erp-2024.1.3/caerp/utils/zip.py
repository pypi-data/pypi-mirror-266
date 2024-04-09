import zipfile
import io

from typing import List

from caerp.models.files import File


def mk_zip(file_models: List[File]) -> io.BytesIO:
    """
    Zip all given File objects in a single archive
    """
    zip_archive = io.BytesIO()
    with zipfile.ZipFile(zip_archive, "w", zipfile.ZIP_DEFLATED, False) as file_buffer:
        for file_model in file_models:
            file_buffer.writestr(file_model.name, file_model.getvalue())
    zip_archive.seek(0)
    return zip_archive
