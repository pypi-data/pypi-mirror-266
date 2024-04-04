import re
from collections import defaultdict
from random import randint
from dataclasses import dataclass, field
import hashlib
import copy
from Exceptions import Messages  # type: ignore
import ValueUtils  # type: ignore
from typing import Dict, Any, List, Tuple


class CoreKeys:
    full_page = "full_page_transcription"


class Locate:
    def __init__(self, document_fields: List[Dict]) -> None:
        self.document_fields = document_fields

    def fields_by_name(self, field_name: str) -> List[Dict]:
        """
        Locate all fields in a HS document based on the field_name
        Returns a list of HS fields
        """
        return list(
            filter(lambda x: x["field_name"] == field_name, self.document_fields)  # type: ignore
        )

    def fields_by_occurrence(
        self, occurence: int, fields: List[Dict] | None = None
    ) -> List[Dict]:
        """
        Locate all fields based on occurrence index value
        Returns a list of HS fields
        """
        if not fields:
            fields = self.document_fields

        return list(
            filter(lambda x: x["occurrence_index"] == occurence, self.document_fields)
        )

    def value_at_position(
        self, field_name: str, occurrence: int, normalised: bool = True
    ) -> str:
        # Gather all fields matching field_name
        filtered_fields = self.fields_by_name(field_name=field_name)
        filtered_occurences = self.fields_by_occurrence(
            occurence=occurrence, fields=filtered_fields
        )

        if filtered_occurences:
            field = filtered_occurences[0]
            if normalised:
                return field.get("transcription_normalized", "")
            else:
                return field.get("transcription", "")
        return ""

    def match_value_any_position(
        self, field_name: str, value: str, threshold: int = 89
    ) -> Tuple[bool, str | None, int | None]:
        """
        takes the field_name and the value then fuzzy matches the value
        against the values in the HS fields

        Returns bool, normalised_value, occurence_index

        When there is no match the expected response is
        False, '', None
        """

        filtered_fields = self.fields_by_name(field_name=field_name)

        for field in filtered_fields:
            normalised_value = field.get("transcription_normalized")
            result = ValueUtils.Compare.string(value, normalised_value, threshold)
            if result:
                return True, normalised_value, field.get("occurence_index")
        return False, None, None


class Document:
    def __init__(self, document: Dict[str, Any])-> None:
        """ """
        self.document = document
        self._fields = document["document_fields"]
        self.page_count = len(document.get("pages", ""))
        self.layout = document.get("layout_name", "")

        self.locate = Locate(self._fields)

    @property
    def fields(self) -> List[Dict]:
        return self._fields

    @fields.setter
    def fields(self, value: Dict[str, Any])->None:
        self._fields.append(value)

    @fields.deleter
    def fields(self)-> None:
        self._fields = self.document["document_fields"]
        self.locate = Locate(self._fields)


class Documents:
    @staticmethod
    def create_filename_array(submission_files: List[Dict])->Dict[str, str]:
        """
        Generate a filename arrary from incoming documents.

        You can get submission_files by running
        HSSubmission.SubmissionFiles(submission).files
        """

        id_fname = {}
        for meta_doc in submission_files:
            url = meta_doc.get("url", "")
            meta_id = url.split("/")[-1]
            filename = meta_doc.get("name", "Filename not found")
            id_fname[str(meta_id)] = filename
        return id_fname

    @staticmethod
    def map_filenames(hs_documents: List[Dict], submission_files: List[Dict])-> List[Dict]:
        """
        Map the filenames from the submission file data to the hs documents
        """
        filenames = Documents.create_filename_array(submission_files)

        updated_hs_documents = copy.deepcopy(hs_documents)

        for document in updated_hs_documents:
            pages = document.get("pages", [{}])
            doc_id = pages[0].get("file_uuid", 0)
            document["filename"] = filenames.get(str(doc_id), "Filename not found")

        return updated_hs_documents

    class FullPage:
        @staticmethod
        def map(hs_documents, full_page_data):
            """
            Map the full page data to the hs document data
            hs_documents is the array of documents under the submission.
            ie submission.documents

            full_page_data is the output of the full page block in its raw
            form.

            returns a modified hs_documents. Each document should have a key "full_page_transcription"
            which contains the segments within the full page
            """

            def reduce_segment(segment):
                """
                Reduces the segment into only needed information
                """
                return {
                    "type": segment.get("type"),
                    "raw_text": segment.get("raw_text"),
                    "text": segment.get("text"),
                }

            def full_page_compress(page):
                """
                Compress all text segments into a single reduced segment
                """

                payload = [
                    reduce_segment(segment) for segment in page.get("segments", [])
                ]
                return payload

            unassigned_pages = full_page_data.get("unassigned_pages", [])

            for document in hs_documents:
                temp_doc = [page.get("id") for page in document.get("pages")]
                doc_segments = [
                    full_page_compress(page)
                    for page_id in temp_doc
                    for page in unassigned_pages
                    if page_id == page.get("id", 0)
                ]
                joined_lists = []
                for x in doc_segments:
                    joined_lists.extend(x)
                document[CoreKeys.full_page] = {"segments": joined_lists}
            return hs_documents

        @staticmethod
        def to_string(hs_document):
            """
            Takes a single HS document and returns the full page transcription
            as a string
            """

            if CoreKeys.full_page not in hs_document:
                raise Exception(Messages.no_full_page_key)

            data = hs_document.get(CoreKeys.full_page)

            segments = data["segments"]
            body = " ".join(
                segment["text"].replace("\n", " ")
                for segment in segments
                if segment["type"] == "text"
            )
            return body
