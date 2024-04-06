# Copyright 2023 Inductor, Inc.
"""Functions for interfacing with the Inductor backend."""
# TODO: Add --verbose mode for printing out the request and response.

import json
import os
from typing import Any, Dict

import httpx

from inductor import config
from inductor.backend_client import wire_model


# TODO: Cleanup these globals.
_MOCK_ENDPOINTS = False


def _post_request(
    endpoint: str, request_body: Dict[str, Any], auth_access_token: str
) -> httpx.Response:
    """POST request to the backend.

    Args:
        endpoint: The endpoint to POST to. Should not begin with a slash.
        request: The request to POST.
        auth_access_token: Auth0 access token.

    Returns:
        The response from the backend.

    Raises:
        RuntimeError: If the response status code is not a successful response
            (i.e., if the response status code is not in the range (200 – 299)).
    """
    response = httpx.post(
        f"{config.settings.inductor_api_url}/api/client/v1/{endpoint}",
        headers={
            "Authorization": f"Bearer {auth_access_token}",
            **(config.settings.custom_request_headers or {}),
        },
        json=json.loads(request_body.model_dump_json()),
    )
    # TODO: These print statements should be avaialbe in --verbose mode.
    # print(f"Request: {request_body.model_dump_json()}")
    # print(f"Response: {response.text}")
    # print(f"Status code: {response.status_code}")
    # print(f"JSON: {response.json()}")
    if response.status_code < 200 or response.status_code >= 300:
        raise RuntimeError(
            f"POST request to `{endpoint}` failed with status code "
            f"{response.status_code} and response text: {response.text}."
        )
    return response


def create_api_key(
    request: wire_model.CreateApiKeyRequest,
    auth_access_token: str):
    """POST request to create an API key.
    
    Args:
        request: CreateApiKeyRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("create-api-key", request, auth_access_token)


def create_test_suite(
    request: wire_model.CreateTestSuiteRequest,
    auth_access_token: str
) -> wire_model.CreateTestSuiteResponse:
    """POST request to create a test suite.

    Args:
        request: CreateTestSuiteRequest object
        auth_access_token: Auth0 access token.
    
    Returns:
        CreateTestSuiteResponse object
    """
    if _MOCK_ENDPOINTS:
        return wire_model.CreateTestSuiteResponse(id=123)
    response = _post_request("create-test-suite", request, auth_access_token)
    return wire_model.CreateTestSuiteResponse(**response.json())


def create_test_suite_run(
    request: wire_model.CreateTestSuiteRunRequest,
    auth_access_token: str
) -> wire_model.CreateTestSuiteRunResponse:
    """POST request to create a test suite run.
    
    Args:
        request: CreateTestSuiteRunRequest object
        auth_access_token: Auth0 access token.
    
    Returns:
        CreateTestSuiteRunResponse object
    """
    if _MOCK_ENDPOINTS:
        return wire_model.CreateTestSuiteRunResponse(
            test_suite_run_id=123,
            test_case_ids=[1, 2, 3, 4, 5, 6],
            quality_measure_ids=[7, 8, 9, 10, 11, 12],
            hparam_spec_ids=[13, 14, 15, 16, 17, 18],
            url="http://localhost:5000/MOCK_URL",
        )
    response = _post_request(
        "create-test-suite-run", request, auth_access_token)
    return wire_model.CreateTestSuiteRunResponse(**response.json())


def log_test_case_execution(
    request: wire_model.LogTestCaseExecutionRequest,
    auth_access_token: str):
    """POST request to log test case execution.

    Args:
        request: LogTestCaseExecutionRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("log-test-case-execution", request, auth_access_token)


def complete_test_suite_run(
    request: wire_model.CompleteTestSuiteRunRequest,
    auth_access_token: str):
    """POST request to complete test suite run.

    Args:
        request: CompleteTestSuiteRunRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("complete-test-suite-run", request, auth_access_token)


def log_llm_program_execution(
    request: wire_model.LogLlmProgramExecutionRequest,
    auth_access_token: str):
    """POST request to log LLM program execution.

    Args:
        request: LogLlmProgramExecutionRequest object
        auth_access_token: Auth0 access token.
    """
    if _MOCK_ENDPOINTS:
        return
    _post_request("log-llm-program-execution", request, auth_access_token)


def create_live_deployment(
    request: wire_model.CreateLiveDeploymentRequest,
    auth_access_token: str) -> wire_model.CreateLiveDeploymentResponse:
    """POST request to create live deployment.

    Args:
        request: `CreateLiveDeploymentRequest` object.
        auth_access_token: Auth0 access token.

    Returns:
        `CreateLiveDeploymentResponse` object.
    """
    response = _post_request(
        "create-live-deployment",
        request,
        auth_access_token)
    return wire_model.CreateLiveDeploymentResponse(**response.json())
