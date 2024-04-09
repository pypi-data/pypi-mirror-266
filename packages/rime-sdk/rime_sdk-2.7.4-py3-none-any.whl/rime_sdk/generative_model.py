"""Library defining the interface to work with generative models."""
from typing import Iterator, Optional

from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.job import GenerativeModelTestJob
from rime_sdk.swagger.swagger_client import (
    ApiClient,
    GenerativeModelTestingApi,
    GenerativetestingGenerativeTestingResult,
    GenerativetestingGetGenerativeModelTestResultsResponse,
    GenerativetestingModelConnectionSpec,
    GenerativetestingStartGenerativeModelTestRequest,
    GenerativetestingStartGenerativeModelTestResponse,
)


class GenerativeModel:
    """The interface to the Generative Model Testing API."""

    def __init__(self, api_client: ApiClient):
        """Initialize the Generative Model interface.

        Args:
            api_client: The API client to use.
        """
        self._api_client = api_client

    def start_test(
        self,
        url: str,
        endpoint_payload_template: str,
        response_json_path: str,
        http_headers: Optional[dict] = None,
    ) -> GenerativeModelTestJob:
        """Start a Generative Model Test.

        Args:
            url: The URL to test.
            http_headers: The HTTP headers to use.
            endpoint_payload_template: The endpoint payload template to use.
            response_json_path: The response JSON path to use.

        Returns:
            GenerativeModelTestJob: The Generative Model Test Job.
        """
        request = GenerativetestingStartGenerativeModelTestRequest(
            connection_spec=GenerativetestingModelConnectionSpec(
                url=url,
                http_headers=http_headers,
                endpoint_payload_template=endpoint_payload_template,
                response_json_path=response_json_path,
            )
        )
        with RESTErrorHandler():
            res: GenerativetestingStartGenerativeModelTestResponse = (
                GenerativeModelTestingApi(
                    self._api_client
                ).generative_model_testing_start_generative_model_test(body=request)
            )
            if res.job_id is None:
                raise ValueError(
                    "Job ID is missing from the response, please try making the request again."
                )

            return GenerativeModelTestJob(self._api_client, res.job_id.uuid)

    def get_results(
        self,
        job_id_uuid: str,
        page_size: Optional[int] = 10,
    ) -> Iterator[GenerativetestingGenerativeTestingResult]:
        """Get the results of a Generative Model Test.

        Args:
            job_id_uuid: The job ID UUID.
            page_size: The number of results per request.  Defaults to 10.

        Returns:
            An iterator of Generative Model Test Results.
        """
        page_token = ""
        with RESTErrorHandler():
            while True:
                res: GenerativetestingGetGenerativeModelTestResultsResponse = (
                    GenerativeModelTestingApi(
                        self._api_client
                    ).generative_model_testing_get_generative_model_test_results(
                        job_id_uuid=job_id_uuid,
                        page_token=page_token,
                        page_size=page_size,
                    )
                )

                yield from res.results

                if not res.has_more:
                    break

                page_token = res.next_page_token
