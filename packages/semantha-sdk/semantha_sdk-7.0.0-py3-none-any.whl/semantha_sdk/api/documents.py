from io import IOBase
from semantha_sdk.model.document import Document
from semantha_sdk.model.document import DocumentSchema
from semantha_sdk.model.documentmode_enum import DocumentmodeEnum
from semantha_sdk.model.type_enum import TypeEnum
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint
from typing import List

class DocumentsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/documents"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documents"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
    ) -> List[Document]:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document for similarity or extraction. The type depends on the Use Case you're in.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    withareas (bool): Gives back the coordinates of referenced area.
    withcontextparagraphs (bool): 
    documentmode (DocumentmodeEnum): 
    withparagraphtype (bool): The type of the paragraph, for example heading, text
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentSchema)
    def post_as_xlsx(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document for similarity or extraction. The type depends on the Use Case you're in.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    withareas (bool): Gives back the coordinates of referenced area.
    withcontextparagraphs (bool): 
    documentmode (DocumentmodeEnum): 
    withparagraphtype (bool): The type of the paragraph, for example heading, text
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.XLSX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()
    def post_as_docx(
        self,
        file: IOBase = None,
        text: str = None,
        type: TypeEnum = None,
        documenttype: str = None,
        withareas: bool = None,
        withcontextparagraphs: bool = None,
        documentmode: DocumentmodeEnum = None,
        withparagraphtype: bool = None,
    ) -> IOBase:
        """
        Creates a list of document models from an input document (pdf, docx, txt, zip, xlsx)
            This service can be used with different accept headers which return the document model as json, pdf or docx. You can send a docx and return it as pdf which is based on the document model.
        Args:
        file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    type (TypeEnum): Choose the structure of a document for similarity or extraction. The type depends on the Use Case you're in.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    withareas (bool): Gives back the coordinates of referenced area.
    withcontextparagraphs (bool): 
    documentmode (DocumentmodeEnum): 
    withparagraphtype (bool): The type of the paragraph, for example heading, text
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "text": text,
                "type": type,
                "documenttype": documenttype,
                "withareas": withareas,
                "withcontextparagraphs": withcontextparagraphs,
                "documentmode": documentmode,
                "withparagraphtype": withparagraphtype,
            },
            headers=RestClient.to_header(MediaType.DOCX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()

    
    
    