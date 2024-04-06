# Copyright 2023 Inductor, Inc.
"""Functionality for test suite execution tasks."""

from concurrent import futures
import contextlib
import datetime
from typing import Any, Dict, Iterator, List, Tuple, Union

import inquirer
import rich
from rich import progress
import typer

from inductor import config
from inductor.backend_client import backend_client, wire_model
from inductor.data_model import data_model
from inductor.execution import execution, quality_measure_execution


@contextlib.contextmanager
def _disable_logger_decorator():
    """Disable the inductor.logger decorator within this context manager.

    Disable the inductor.logger decorator by setting
    `execution.logger_decorator_enabled` to False. On exit, restore the
    original value of `execution.logger_decorator_enabled`.
    """
    orig_logger_decorator_enabled = execution.logger_decorator_enabled
    try:
        execution.logger_decorator_enabled = False
        yield
    finally:
        execution.logger_decorator_enabled = orig_logger_decorator_enabled


def _execute_test_case(
    test_suite_run_id: int,
    llm_program_fully_qualified_name: str,
    test_case: data_model.TestCase,
    test_case_id: int,
    test_case_replica_index: int,
    quality_measure_list: List[data_model.QualityMeasure],
    quality_measure_ids: List[int],
    hparams: Dict[str, Any],
    auth_access_token: str,
) -> Tuple[
    wire_model.LogTestCaseExecutionRequest,
    List[Dict[str, Union[
        int, str, wire_model.QualityMeasureExecutionDetails]]]]:
    """Run a test case and evaluate its quality measures.

    Sends the output of the test case and the outputs of the quality measures
    to the backend server.

    Args:
        test_suite_run_id: ID of test suite run.
        llm_program_fully_qualified_name: Fully qualified name of LLM program.
        test_case: Test case.
        test_case_id: ID of test case.
        test_case_replica_index: Index of test case replica.
        quality_measure_list: List of quality measures.
        quality_measure_ids: IDs of quality measures.
        hparams: Mapping from hyperparameter names to values.
        auth_access_token: Auth0 access token.
    
    Returns:
        A tuple of the LogTestCaseExecutionRequest and a list of invalid
            quality measures if any. Each invalid quality measure is a
            Dictionary with the following keys:
                "id": ID of quality measure.
                "name": Name of quality measure.
                "execution_details": wire_model.QualityMeasureExecutionDetails
                    object.
    """
    started_at = datetime.datetime.now(datetime.timezone.utc)

    llm_program_stdout = None
    llm_program_stderr = None
    llm_program_error = None
    llm_program_output = None
    # Note: we use backslashes to split the `with` clause immediately below,
    # rather than enclosing in parentheses, because enclosing in parentheses
    # apparently causes a SyntaxError when running in Python 3.8.
    # pylint: disable-next=protected-access
    with execution.capture_stdout_stderr(suppress=True) as (stdout, stderr), \
        execution.capture_logged_values() as logged_values, \
        _disable_logger_decorator(), \
        execution.set_hparams(hparams):
        try:
            # Run the LLM program.
            llm_program = data_model.LazyCallable(
                llm_program_fully_qualified_name)
            llm_program_output = llm_program(**test_case.inputs)
            if isinstance(llm_program_output, Iterator):
                llm_program_output = list(llm_program_output)
                if all(isinstance(value, str) for value in llm_program_output):
                    llm_program_output = "".join(llm_program_output)

        except Exception as error:  # pylint: disable=broad-except
            llm_program_error = str(error)

        llm_program_stdout = stdout.getvalue()
        llm_program_stderr = stderr.getvalue()

    ended_at = datetime.datetime.now(datetime.timezone.utc)

    # If the LLM program completed without error, run the executable quality
    # measures.
    if llm_program_error is None:
        direct_evaluations, invalid_quality_measures = (
            quality_measure_execution.execute_quality_measures(
                test_case=test_case,
                llm_program_output=llm_program_output,
                quality_measure_list=quality_measure_list,
                quality_measure_ids=quality_measure_ids))
    else:
        direct_evaluations = []
        invalid_quality_measures = []

    request_object = wire_model.LogTestCaseExecutionRequest(
        test_suite_run_id=test_suite_run_id,
        test_case_id=test_case_id,
        test_case_replica_index=test_case_replica_index,
        execution_details=wire_model.ExecutionDetails(
            mode="CLI",
            inputs=test_case.inputs,
            hparams=hparams or None,
            output=llm_program_output,
            error=llm_program_error,
            stdout=llm_program_stdout,
            stderr=llm_program_stderr,
            execution_time_secs=(ended_at - started_at).total_seconds(),
            started_at=started_at,
            ended_at=ended_at,
            logged_values=logged_values or None,
            direct_evaluations=direct_evaluations or None,
        )
    )

    backend_client.log_test_case_execution(request_object, auth_access_token)
    return request_object, invalid_quality_measures


@contextlib.contextmanager
def _manage_test_suite_run(
    test_suite: data_model.TestSuite,
    auth_access_token: str) -> wire_model.CreateTestSuiteRunResponse:
    """Send requests to the server to manage the creation/completion of a run.
    
    Send a request to the server to create a test suite run. Then, yield the
    response, which contains test suite run metadata. On exit, send a request
    to the server to mark the test suite run as complete.

    Args:
        test_suite: Test suite.
        auth_access_token: Auth0 access token.

    Yields:
        CreateTestSuiteRunResponse object.
    """
    test_suite_run = test_suite._get_run_request()  # pylint: disable=protected-access
    test_suite_run_metadata = backend_client.create_test_suite_run(
        test_suite_run, auth_access_token)
    try:
        yield test_suite_run_metadata
    finally:
        backend_client.complete_test_suite_run(
            wire_model.CompleteTestSuiteRunRequest(
                test_suite_run_id=
                    test_suite_run_metadata.test_suite_run_id,
                ended_at=
                    datetime.datetime.now(datetime.timezone.utc)),
            auth_access_token)


def execute_test_suite(
    test_suite: data_model.TestSuite,
    auth_access_token: str,
    *,
    prompt_open_results: bool = False):
    """Execute a test suite.
    
    Execute a test suite while displaying relevant information to the user,
    including a progress bar.
    
    Args:
        test_suite: Test suite to execute.
        auth_access_token: Auth0 access token.
        prompt_open_results: Whether to prompt the user to open the test
            suite run results in a browser.
    """
    # Note: we use backslashes to split the `with` clause immediately below,
    # rather than enclosing in parentheses, because enclosing in parentheses
    # apparently causes a SyntaxError when running in Python 3.8.
    with futures.ProcessPoolExecutor(
            max_workers=test_suite.config.parallelize) as executor, \
        _manage_test_suite_run(
            test_suite, auth_access_token) as test_suite_run_metadata:
        test_case_futures = []
        hparam_combinations = execution.get_hparams_combinations(
            test_suite.hparam_specs)
        for test_case_replica_index in range(test_suite.config.replicas):
            for hparams in hparam_combinations:
                for test_case, test_case_id in zip(
                    test_suite.test_cases,
                    test_suite_run_metadata.test_case_ids):
                    test_case_futures.append(executor.submit(
                        _execute_test_case,
                        test_suite_run_id=
                            test_suite_run_metadata.test_suite_run_id,
                        llm_program_fully_qualified_name=
                            test_suite.config.llm_program,
                        test_case=test_case,
                        test_case_id=test_case_id,
                        test_case_replica_index=test_case_replica_index,
                        quality_measure_list=test_suite.quality_measures,
                        quality_measure_ids=
                            test_suite_run_metadata.quality_measure_ids,
                        hparams=hparams,
                        auth_access_token=auth_access_token,
                    ))

        typer.echo(f"Go to {test_suite_run_metadata.url} to view results.")
        if prompt_open_results:
            open_url = inquirer.confirm(
                message="Open in browser?", default=True)
            if open_url:
                typer.launch(test_suite_run_metadata.url)

        # Display progress bar and optionally print test outputs.
        with progress.Progress() as progress_bar:
            progress_task = progress_bar.add_task(
                "Test Cases",
                total=(test_suite.config.replicas *
                        len(test_suite.test_cases) *
                        len(hparam_combinations)))

            for future in futures.as_completed(test_case_futures):
                progress_bar.advance(progress_task)
                test_output, invalid_quality_measures = future.result()
                if test_output.execution_details.error is not None:
                    progress_bar.console.print(
                        "\n[red][bold][ERROR] Test case execution "
                        "raised an exception.[/bold] The following "
                        "execution will be recorded as FAILED and "
                        "quality measures will not be evaluated:[/red]")
                    progress_bar.console.print(test_output)
                elif config.verbose:
                    progress_bar.console.print(test_output)
                if invalid_quality_measures:
                    progress_bar.console.print(
                        "\n[red][bold][ERROR] One or more quality "
                        "measures raised an exception or returned an "
                        "invalid value.[/bold] The following quality "
                        "measures will not be recorded as part of this "
                        "test case execution:[/red]")
                    progress_bar.console.print(invalid_quality_measures)

        rich.print("Run complete.")
