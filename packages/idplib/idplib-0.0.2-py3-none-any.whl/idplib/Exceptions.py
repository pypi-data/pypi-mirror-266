from dataclasses import dataclass


@dataclass
class Messages:
    no_full_page_key = """
    Key full_page_transcription is missing, please ensure Documents.Fullpage.map is run
    Please note you may need a full page block in the HS manifest to enable this fuctionality
    """
