import inspect
import json


class SubmissionFiles:
    def __init__(self, submission):
        """
        Take the HS submission and extract the submission
        data
        """
        submission_id_ref = submission["id"]
        proxy = inspect.stack()[1].frame.f_locals["proxy"]

        r = proxy.sdm_get(
            f"api/v5/submissions/{submission_id_ref}?flat=False", timeout=10
        )
        self.data = r.json()

    @property
    def files(self):
        """
        Returns the submission files
        """
        return self.data.get("submission_files")
