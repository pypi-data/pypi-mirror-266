"""
Pdf storage service implementation (interface ITaskPdfStorageService)
"""
import logging
import hashlib
import io
from PyPDF4 import PdfFileMerger
from caerp.models.files import File
from caerp.export.task_pdf import (
    task_bulk_pdf,
    task_pdf,
)


logger = logging.getLogger(__name__)


class PdfFileDepotStorageService:
    """
    This class implements the
    :class:`caerp.interfaces.ITaskPdfStorageService`
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        if context is None:
            self.context = request.context

    def store_pdf(self, filename, pdf_buffer):
        """
        Stores the pdf on disk if needed

        :param obj pdf_buffer: instance of :class:`io.BytesIO`
        :param str filename: The name of the pdf file
        """
        if self.context.status == "valid":
            logger.info("Storing PDF data for document {}".format(self.context))
            pdf_buffer.seek(0)
            pdf_datas = pdf_buffer.read()
            pdf_buffer.seek(0)
            pdf_hash = hashlib.sha1(pdf_datas).hexdigest()
            size = len(pdf_datas)
            logger.info("Associated PDF hash : {}".format(pdf_hash))
            self.context.pdf_file = File(
                name=filename,
                mimetype="application/pdf",
                size=size,
                description="Fichier Pdf généré",
            )
            self.context.pdf_file_hash = pdf_hash
            self.context.pdf_file.data = pdf_datas
            self.request.dbsession.merge(self.context)
        else:
            logger.debug(
                "We don't persist the PDF data : {} status is "
                "not valid".format(self.context)
            )

    def retrieve_pdf(self):
        """
        Retrieve the pdf and returns it as a data buffer
        """
        logger.debug("Retrieving PDF datas for {}".format(self.context))
        data = None
        if self.context.pdf_file is not None:
            logger.debug(
                "Retrieving a cached PDF with hash : {}".format(
                    self.context.pdf_file_hash
                )
            )
            try:
                data = self.context.pdf_file.data_obj
                if not data:
                    raise IOError()
            except IOError:
                logger.exception(
                    "The file {} is in the database but can't be retrieved "
                    "from disk : Data corruption ?".format(self.context.pdf_file.id)
                )
                data = None
        return data

    def get_bulk_pdf(self, tasks):
        """
        Produce a Large pdf containing the pdf of all given tasks
        Excludes CGV related informations

        :param list tasks: List of Task instances
        :returns: A pdf as a bytes data buffer
        """
        return task_bulk_pdf(tasks, self.request)

    def set_task(self, task):
        """
        Set task (if it's different from the current context)
        """
        self.context = task


# fix tests pdf


class PdfDevStorageService:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        if context is None:
            self.context = request.context

    def store_pdf(self, filename, pdf_buffer):
        pass

    def retrieve_pdf(self):
        return None

    def get_bulk_pdf(self, tasks):
        result = io.BytesIO()
        writer = PdfFileMerger()
        for task in tasks:
            pdf = task_pdf(task, self.request)
            writer.append(pdf)
        writer.write(result)
        return result

    def set_task(self, task):
        self.context = None
