# Copyright 2023 Inductor, Inc.
"""Functionality for live execution tasks."""

from concurrent import futures
import contextlib
import contextvars
import datetime
import functools
import inspect
import random
import traceback
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from inductor import auth_session, config
from inductor.backend_client import backend_client, wire_model
from inductor.data_model import data_model
from inductor.execution import execution, quality_measure_execution


# Stores a boolean flag indicating whether the current LLM program execution is
# the primary (top-level) execution. This flag allows nested functions that are
# decorated with the logger decorator to be collapsed into a single LLM program
# execution, without sending duplicate data to the backend.
_primary_execution = contextvars.ContextVar("active_execution", default=True)
# Executor for executing quality measures on live executions (so that the user
# does not have to wait for the quality measures to complete before receiving
# their LLM program's output). This executor is created lazily (i.e., when
# the logger decorator first evaluates quality measures) and is re-used for
# all subsequent quality measure evaluations. The executor is not shut down
# until the program exits. Note that multiprocessing for live executions (and
# thus this executor) is only used if
# `config.settings.inductor_logger_use_multiprocessing` is True.
_process_pool_executor = None


@contextlib.contextmanager
def _manage_executions():
    """Manage the state of the primary execution context variable.

    Manage the state of the primary execution context variable
    (_primary_execution). If the variable is initially True, it is set to
    False and True is yielded. If the variable is initially False, False is
    yielded. On exit, the variable is restored to its original value.

    The purpose of this context manager is to allow the logger decorator to
    determine whether it is the primary (top-level) execution. This is
    necessary because the logger decorator should only send data to the
    backend if it is the primary execution. For example, when the logger
    decorator decorates a function that is called by another function also
    decorated with the logger decorator, the logger decorator should not send
    data to the backend during the inner function call.

    Yields:
        True if the primary execution context variable was True, False
        otherwise.
    """
    primary_execution = _primary_execution.get()
    if primary_execution:
        _primary_execution.set(False)
    try:
        yield primary_execution
    finally:
        _primary_execution.set(primary_execution)


def _complete_live_execution(
    *,
    primary_execution: bool,
    inputs: Optional[Dict[str, Any]] = None,
    hparams: Optional[Dict[str, Any]] = None,
    output: Optional[Any] = None,
    error_str: Optional[str] = None,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    started_at: datetime.datetime,
    logged_values: List[wire_model.LoggedValue],
    program_details: wire_model.ProgramDetails,
    live_deployment_config_id: Optional[int],
    quality_measure_components: List[data_model.QualityMeasure],
    quality_measure_ids: List[int],
    auth_access_token: str,
):
    """Complete a LLM program live execution.

    If the LLM program execution is the primary execution:
        - Execute any given quality measures on the LLM program output.
        - Send the execution data to the backend.
    Otherwise:
        - Call the Inductor client's `log()` function to log this execution as
            part of the current overarching primary execution.

    Args:
        primary_execution: Whether this is the primary execution.
        inputs: Input arguments to the LLM program.
        hparams: Hyperparameters set for the LLM program execution.
        output: Output of the LLM program. If the output is an
            `execution.IteratorWrapper` the values yielded by the iterator
            will be used as the output.
        error_str: Error (in string form) raised by the LLM program, if any.
        stdout: Contents of stdout.
        stderr: Contents of stderr.
        started_at: Time at which the LLM program execution started.
        logged_values: Values logged by the LLM program.
        program_details: Details of the LLM program.
        live_deployment_config_id: ID of the live deployment configuration
            that is associated with the LLM program, if any.
        quality_measure_components: Quality measures to be evaluated for the LLM
            program, if `primary_execution` is True.
        quality_measure_ids: IDs of the quality measures to be evaluated. The
            order of the IDs should match the order of the quality measures in
            `quality_measure_components`.
        auth_access_token: Auth0 access token to be used to authenticate
            requests to the backend.
    """
    ended_at = datetime.datetime.now(datetime.timezone.utc)

    if isinstance(output, execution.IteratorWrapper):
        # If the output is the result of an iterator, get the actual
        # output value and any error that occurred during the iteration.
        iterator_wrapper = output
        output = iterator_wrapper._get_completed_values()  # pylint: disable=protected-access
        assert error_str is None, (
            "An error occurred during the initial execution of the LLM "
            "program, but the output was an iterator. We do not expect an "
            "output from a function that raises an error.")
        error = iterator_wrapper._iteration_error  # pylint: disable=protected-access
        error_str = str(error) if error is not None else None

    if primary_execution:

        def log_live_execution(
            direct_evaluations: Optional[List[
                wire_model.DirectEvaluation]] = None,
            invalid_quality_measures: Optional[
                List[Dict[
                    str,
                    Union[int, str, wire_model.QualityMeasureExecutionDetails]
                ]]] = None):
            """Log the LLM program execution.
            
            Args:
                direct_evaluations: Direct evaluations of the LLM program
                    execution.
                invalid_quality_measures: Quality measures that could not be
                    evaluated.
            """
            # Add any invalid quality measure results to the LLM program
            # execution's logged values.
            if invalid_quality_measures is not None:
                for invalid_quality_measure in invalid_quality_measures:
                    logged_values.append(wire_model.LoggedValue(
                        value=
                        data_model.deepcopy_or_str(invalid_quality_measure),
                        description="Invalid quality measure",
                        after_complete=True))

            backend_client.log_llm_program_execution(
                wire_model.LogLlmProgramExecutionRequest(
                    program_details=program_details,
                    execution_details=wire_model.ExecutionDetails(
                        mode="DEPLOYED",
                        inputs=inputs if inputs else {},
                        hparams=hparams or None,
                        output=output,
                        error=error_str,
                        stdout=stdout,
                        stderr=stderr,
                        execution_time_secs=(
                            ended_at - started_at).total_seconds(),
                        started_at=started_at,
                        ended_at=ended_at,
                        logged_values=logged_values or None,
                        direct_evaluations=direct_evaluations,
                        live_deployment_config_id=live_deployment_config_id,)
                    ),
                auth_access_token)

        # Execute quality measures, if any.
        if (config.settings.inductor_logger_use_multiprocessing and
            quality_measure_components):
            global _process_pool_executor  # pylint: disable=global-variable-not-assigned
            # Create the process pool executor if it does not exist.
            if _process_pool_executor is None:
                # While most non-LLM quality measures are expected to
                # be fast and CPU bound, LLM quality measures are
                # expected to be slow and IO bound. Therefore, to
                # prevent potential bottlenecks during the evaluation
                # of LLM quality measures, we set the max workers
                # relatively high (10).
                _process_pool_executor = futures.ProcessPoolExecutor(
                    max_workers=10)
            future = _process_pool_executor.submit(
                quality_measure_execution.execute_quality_measures,
                test_case=data_model.TestCase(inputs),
                llm_program_output=output,
                quality_measure_list=quality_measure_components,
                quality_measure_ids=quality_measure_ids,
            )
            future.add_done_callback(
                lambda future: log_live_execution(*future.result()))
        else:
            direct_evaluations, invalid_quality_measures = (
                quality_measure_execution.execute_quality_measures(
                    test_case=data_model.TestCase(inputs),
                    llm_program_output=output,
                    quality_measure_list=quality_measure_components,
                    quality_measure_ids=quality_measure_ids,
                ))
            log_live_execution(direct_evaluations, invalid_quality_measures)

    else:
        execution.log(
            {
                "llm_program": program_details.fully_qualified_name,
                "inputs": inputs if inputs else {},
                "output": output
            },
            name="Nested LLM program execution")


def logger(
    # NOTE: The function is optional to allow for the decorator to be used
    # with or without parentheses.
    original_function: Optional[Callable] = None,
    *,
    quality_measures: Optional[Union[
        data_model.QualityMeasure,
        List[data_model.QualityMeasure],
        data_model.YAMLFilePath]] = None,
    hparam_specs: Optional[Union[
        data_model.HparamSpec,
        List[data_model.HparamSpec],
        data_model.YAMLFilePath]] = None,
) -> Callable:
    """Log the inputs, outputs, and inductor.log calls of the given function.

    Use `logger` as a decorator to automatically log the arguments and return
    value of, as well as calls to inductor.log within, the decorated function.

    For example:
        @inductor.logger
        def hello_world(name: str) -> str:
            inductor.log(len(name), description="name length")
            return f"Hello {name}!"

    Args:
        original_function: Function to wrap. This argument should not
            be explicitly set when using @decorator syntax.
        quality_measures: Quality measures to be used to evaluate the outputs
            of the wrapped function. Quality measures can be passed in
            the following ways:
            - As an individual quality measure or a list of quality measures.
            - As a path to a YAML file specifying quality measures in the same
                format as used in Inductor test suite YAML files. (A test
                suite YAML file path would meet this requirement.)
        hparam_specs: Specifications of hyperparameters to be used
            when executing the wrapped function.  If and when
            `inductor.hparam(name, default_value)` is called within the
            wrapped function, the value that is returned will be determined
            by `hparam_specs`:
            - If `hparam_specs` contains an HparamSpec having the
                given name (per each HparamSpec's `name` field), then
                a random value from the list given by the HparamSpec's
                `values` field is returned.  Set the HparamSpec's `values`
                field to a list containing a single element to lock the
                hyperparameter to a specific value, or instead use a list
                of values to A/B(/C/etc) test among different values.
            - If `hparam_specs` does not contain an HparamSpec having the
                given name (per each HparamSpec's `name` field), then
                `inductor.hparam(name, default_value)` returns `default_value`.
            Hyperparameter specifications can be passed via `hparam_specs`
            in the following ways:
            - As an individual hyperparameter specification or a list of
                hyperparameter specifications.
            - As a path to a YAML file giving hyperparameter specifications
                in the same format as used in Inductor test suite YAML
                files. (A test suite YAML file path would meet this
                requirement.)

    Returns:
        Decorator.
    """
    def _logger(func: Callable) -> Callable:
        try:
            logger_auth_session = auth_session.get_auth_session()
            # Next line is present to check that an access token can be
            # successfully obtained
            logger_auth_session.access_token  # pylint: disable=pointless-statement
            llm_program = data_model.LazyCallable(func)
            program_details = llm_program.get_program_details()
        except Exception as error:  # pylint: disable=broad-except
            traceback.print_exc()
            print(
                "[ERROR] Exception occurred during setup of inductor.logger. "
                "No data will be sent to Inductor through the logger "
                f"decorator for this session. {error}")
            return func

        # We only attempt to create a live deployment configuration on the
        # first call to the decorated function. Creating a live deployment
        # configuration is idempotent, so it is acceptable to accidentally
        # attempt to create multiple live deployment configurations if the
        # user calls the decorated function multiple times (and a race
        # condition occurs with the `attempt_live_deployment_config_creation`
        # flag).
        # We intentionally create live deployment configurations lazily
        # (i.e., on the first call to the decorated function) instead of
        # eagerly (i.e., when the logger decorator is called) to avoid
        # creating live deployment configurations when functions are imported
        # but not called.
        attempt_live_deployment_config_creation = True
        # Once a live deployment configuration is created, we store the
        # configuration locally in `logger_config` to avoid needing to
        # attempt to create the configuration again on subsequent calls to the
        # decorated function.
        logger_config = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if execution.logger_decorator_enabled:
                # Variables from the outer scope that we need to modify.
                nonlocal logger_config
                nonlocal attempt_live_deployment_config_creation

                func_result = None
                func_error = None
                func_completed = False

                try:
                    if attempt_live_deployment_config_creation:

                        if quality_measures is not None:
                            # Collect all the given quality measures.
                            # TODO:
                            # https://github.com/inductor-hq/saas/issues/324
                            # - Remove duplicates from
                            # quality_measure_components.
                            quality_measure_components = (
                                data_model.get_test_suite_components(
                                    quality_measures)["quality_measures"])
                            logger_config["quality_measure_components"] = (
                                quality_measure_components)
                        if hparam_specs is not None:
                            # Collect all the given hyperparameter
                            # specifications.
                            # TODO:
                            # https://github.com/inductor-hq/saas/issues/324
                            # - Remove duplicates from hparam_spec_components.
                            hparam_spec_components = (
                                data_model.get_test_suite_components(
                                    hparam_specs)["hparam_specs"])
                            logger_config["hparam_spec_components"] = (
                                hparam_spec_components)

                        if len(logger_config) > 0:
                            # If `logger_config` is not empty, then parameters
                            # were passed to the decorated function and we
                            # need to create a live deployment configuration.
                            quality_measures_dict_list = [
                                quality_measure.model_dump()
                                for quality_measure in
                                    logger_config.get(
                                        "quality_measure_components", [])
                            ]
                            hparam_specs_dict_list = [
                                hparam_spec.model_dump()
                                for hparam_spec in logger_config.get(
                                    "hparam_spec_components", [])
                            ]

                            response = \
                                backend_client.create_live_deployment(
                                    wire_model.CreateLiveDeploymentRequest(
                                        program_details=program_details,
                                        quality_measures=(
                                            quality_measures_dict_list
                                            if quality_measures_dict_list
                                            else None),
                                        hparam_specs=(
                                            hparam_specs_dict_list
                                            if hparam_specs_dict_list
                                            else None
                                        ),
                                    ),
                                    logger_auth_session.access_token)

                            quality_measure_ids = response.quality_measure_ids
                            if quality_measure_ids:
                                logger_config["quality_measure_ids"] = (
                                    quality_measure_ids)

                            live_deployment_config_id = (
                                response.live_deployment_config_id)
                            logger_config["live_deployment_config_id"] = (
                                live_deployment_config_id)

                        attempt_live_deployment_config_creation = False

                    live_deployment_config_id = logger_config.get(
                        "live_deployment_config_id", None)
                    quality_measure_components = logger_config.get(
                        "quality_measure_components", [])
                    quality_measure_ids = logger_config.get(
                        "quality_measure_ids", [])
                    hparam_spec_components = logger_config.get(
                        "hparam_spec_components", [])
                    hparams = {
                        hs.name: random.choice(hs.values)
                        for hs in hparam_spec_components}

                    # Notes regarding the `with` clause immediately below:
                    # - We use backslashes to split the clause, rather than
                    # enclosing in parentheses, because enclosing in
                    # parentheses apparently causes a SyntaxError when running
                    # in Python 3.8.
                    # - We actually don't need to capture stdout and stderr if
                    # we are not in the primary execution. However, since
                    # stdout and stderr are not suppressed, the user will not
                    # be impacted, and we allow stdout and stdout to be
                    # captured nonetheless to simplify the code.
                    with execution.capture_logged_values() as logged_values, \
                        _manage_executions() as primary_execution, \
                        execution.capture_stdout_stderr(
                            suppress=False) as (stdout, stderr), \
                        execution.set_hparams(hparams, primary_execution):

                        # Get input arguments using the function's signature.
                        signature = inspect.signature(func)
                        bound_arguments = signature.bind(*args, **kwargs)
                        bound_arguments.apply_defaults()
                        processed_input_args = {}
                        for key, value in bound_arguments.arguments.items():
                            processed_input_args[key] = (
                                data_model.deepcopy_or_str(value))

                        started_at = datetime.datetime.now(
                            datetime.timezone.utc)

                        try:
                            func_result = func(*args, **kwargs)
                        except Exception as e:  # pylint: disable=broad-except
                            func_error = e
                        finally:
                            func_completed = True

                        execution_details = {
                            "primary_execution": primary_execution,
                            "inputs": processed_input_args,
                            "hparams": hparams,
                            "error_str": (
                                str(func_error)
                                if func_error is not None else None
                            ),
                            "stdout": stdout.getvalue(),
                            "stderr": stderr.getvalue(),
                            "started_at": started_at,
                            "logged_values": logged_values,
                            "program_details": program_details,
                            "live_deployment_config_id":
                                live_deployment_config_id,
                            "quality_measure_components":
                                quality_measure_components,
                            "quality_measure_ids": quality_measure_ids,
                            "auth_access_token": (
                                logger_auth_session.access_token),
                        }

                        if isinstance(func_result, Iterator):
                            # We cannot assume that the iterator can be
                            # re-used. Therefore we return a wrapper for the
                            # iterator that captures returned values and will
                            # complete the execution when the iterator is
                            # exhausted.
                            return execution.IteratorWrapper(
                                func_result,
                                stop_signal_handler=_complete_live_execution,
                                stop_signal_handler_kwargs=execution_details,
                                iterator_wrapper_error_message=(
                                    "[ERROR] Exception occurred during "
                                    "iteration of the LLM program result. No "
                                    "data will be sent to Inductor as part of "
                                    "this LLM program execution. "
                                ))

                        execution_details["output"] = (
                            data_model.deepcopy_or_str(func_result))
                        _complete_live_execution(**execution_details)

                        if func_error is not None:
                            raise func_error  # pylint: disable=raise-missing-from
                        return func_result

                except Exception as decorator_error:  # pylint: disable=broad-except
                    traceback.print_exc()
                    print(
                        f"[ERROR] Exception occurred in inductor.logger. No "
                        f"data will be sent to Inductor as part of this LLM "
                        f"program execution. {decorator_error}")
                    if func_completed:
                        # If the LLM program execution completed, there is no
                        # need to rerun the LLM program. Rerunning the LLM
                        # program could significantly hurt performance or could
                        # cause wider issues if the LLM program has side
                        # effects.
                        if func_error is not None:
                            raise func_error  # pylint: disable=raise-missing-from
                        return func_result
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper

    if original_function is not None:
        return _logger(original_function)

    return _logger
