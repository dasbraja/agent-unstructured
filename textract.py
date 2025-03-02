"""Textract Connector for text/table extraction from documents."""

import time
from typing import List, Union

import boto3
from textractcaller.t_call import (
    get_full_json,
    get_job_response,
)
from textractor import Textractor
from textractor.data.constants import TextractAPI, TextractFeatures
from textractor.parsers.response_parser import parse
from textractor.utils.results_utils import get_full_json_from_output_config, results_exist


class TextractDocumentAnalysis():
    """
    A class to analyze documents using AWS Textract's document analysis features.


    :param aws_profile_name: The AWS profile name to use for authentication.
    :param source: The S3 URI of the document to be analyzed.
    """

    def __init__(self, region: str, source: str) -> None:
        self.source = source
        #self.extractor = Textractor(profile_name=aws_profile_name)
        self.extractor = Textractor(region_name=region)
        self._analyzed_document = None
        self._lazy_document = None
        self._job_response = None

    def analyze_document(self, features: Union[List[str], None] = None) -> None:
        """Analyze the document using specified features.

        :param features: A list of features to analyze, such as "tables", "forms", "signatures".
                         If None, all features will be analyzed.
        :raises AssertionError: If any feature in the list is not recognized.
        """
        # Map the feature names to TextractFeatures
        features_map = {
            "tables": TextractFeatures.TABLES,
            "forms": TextractFeatures.FORMS,
            "signatures": TextractFeatures.SIGNATURES,
        }
        if features is not None:
            # Check if all specified features are recognized
            assert all(feature.lower() in features_map for feature in features)
        if self._lazy_document is None:
            # Start the document analysis with the specified features
            self._lazy_document = self.extractor.start_document_analysis(
                self.source, features=[features_map[feature.lower()] for feature in features]
            )

    def get_response(self):
        """
        Retrieve the Textract job response as a JSON object.

        :returns: The Textract job response.
        :raises Exception: If the Textract job fails or exceeds the polling interval.
        """
        if self._analyzed_document is None:
            if self._lazy_document._document is None:
                if self._lazy_document._output_config:
                    # If output configuration exists, poll the S3 bucket for results
                    s3_client = boto3.client("s3")
                    start = time.time()
                    response = None
                    while not results_exist(
                        self._lazy_document.job_id,
                        self._lazy_document._output_config.s3_bucket,
                        self._lazy_document._output_config.s3_prefix,
                        s3_client,
                    ):
                        # Sleep for the polling interval before checking again
                        time.sleep(self._lazy_document._s3_polling_interval)
                        if time.time() - start > self._lazy_document._textract_polling_interval:
                            # If polling interval exceeded, get job response directly
                            self._job_response = get_job_response(
                                job_id=self._lazy_document.job_id,
                                textract_api=TextractAPI.TextractAPI_to_Textract_API(self._lazy_document._api)
                                if isinstance(self._lazy_document._api, TextractAPI)
                                else self._lazy_document._api,
                                boto3_textract_client=self._lazy_document._textract_client,
                            )
                            job_status = self._job_response["JobStatus"]
                            if job_status == "IN_PROGRESS":
                                start = time.time()
                                self._job_response = None
                                continue
                            elif job_status == "SUCCEEDED" and "NextToken" in response:
                                # Get the full JSON response if the job succeeded with a NextToken
                                self._job_response = get_full_json(
                                    self._lazy_document.job_id,
                                    TextractAPI.TextractAPI_to_Textract_API(self._lazy_document._api)
                                    if isinstance(self._lazy_document._api, TextractAPI)
                                    else self._lazy_document._api,
                                    self._lazy_document._textract_client,
                                    job_done_polling_interval=1,
                                )
                                break
                            elif job_status == "SUCCEEDED":
                                break
                            else:
                                raise Exception(f"Job failed with status: {job_status}\n{response}")

                    if not self._job_response:
                        # Get full JSON from output config if response is not already set
                        self._job_response = get_full_json_from_output_config(
                            self._lazy_document._output_config,
                            self._lazy_document.job_id,
                            s3_client,
                        )
                else:
                    if not self._lazy_document._textract_client:
                        self._lazy_document._textract_client = boto3.client("textract")
                    # Get full JSON from Textract API
                    self._job_response = get_full_json(
                        self._lazy_document.job_id,
                        TextractAPI.TextractAPI_to_Textract_API(self._lazy_document._api)
                        if isinstance(self._lazy_document._api, TextractAPI)
                        else self._lazy_document._api,
                        self._lazy_document._textract_client,
                        job_done_polling_interval=self._lazy_document.textract_polling_interval,
                    )
        return self._job_response

    def get_document(self):
        """Retrieve the analyzed document.

        :returns: The analyzed document.
        :raises Exception: If the Textract job fails or exceeds the polling interval.
        """
        self._job_response = self.get_response()
        # Parse the response to get the document
        self._lazy_document._document = parse(self._job_response)
        if self._lazy_document._images is not None:
            for i, page in enumerate(self._lazy_document._document.pages):
                # Attach images to the document pages if available
                page.image = self._lazy_document._images[i]
        self._analyzed_document = self._lazy_document._document
        return self._analyzed_document
