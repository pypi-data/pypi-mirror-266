# Copyright 2023 Inductor, Inc.
"""Functionality for executing quality measures."""

import traceback
from typing import Any, Dict, List, Tuple, Union

import openai
import tiktoken

from inductor.backend_client import wire_model
from inductor.data_model import data_model
from inductor.execution import execution


class Inputs(dict):
    """A dictionary that allows access to its keys as attributes."""

    def __getattribute__(self, key: str) -> Any:
        """Return the value corresponding to key in this dict.
        
        Args:
            key: The key to access.

        Raises:
            AttributeError: If the key does not exist in this dict.
        """
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc


def _openai_llm_quality_measure(
    output: str,
    inputs: Inputs,
    test_case: wire_model.TestCase,
    quality_measure: wire_model.QualityMeasure,
    model: str,
    prompt: str
) -> str:
    """Evaluate an LLM-powered quality measure using the OpenAI API.
    
    Args:
        output: The output of the execution of a LLM program.
        inputs: The inputs to the LLM program execution that produced output.
        test_case: The test case that served as input to the LLM program
            execution that produced output.
        quality_measure: The quality measure being evaluated.
        model: The model to use in the LLM powered quality measure.
        prompt: The prompt for the LLM powered quality measure.

    Returns:
        The result of evaluating the quality measure.
    """
    client = openai.OpenAI()
    accepted_outputs = []
    evaluation_type_prompt = ""
    if quality_measure.evaluation_type == "BINARY":
        evaluation_type_prompt = (
            "Output must be *ONLY* one of Y (for YES) or N (for NO).")
        accepted_outputs = ["Y", "N"]
    elif quality_measure.evaluation_type == "RATING_INT":
        evaluation_type_prompt = (
            "Output must be *ONLY* an integer from 1 through 5.")
        accepted_outputs = ["1", "2", "3", "4", "5"]

    encoding = tiktoken.encoding_for_model(model)
    max_tokens = 1
    logit_bias = {}
    for accepted in accepted_outputs:
        tokens = encoding.encode(accepted)
        max_tokens = max(max_tokens, len(tokens))
        logit_bias.update({token: 100 for token in tokens})

    execution_results = {
        "output": output, "inputs": inputs, "test_case": test_case}
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt.format_map(execution_results)},
            {"role": "system", "content": evaluation_type_prompt}
        ],
        model=model,
        max_tokens=max_tokens,
        logit_bias=logit_bias)
    return chat_completion.choices[0].message.content


def _execute_quality_measure_function(
    llm_program_output: Any,
    quality_measure: data_model.QualityMeasure,
    test_case: data_model.TestCase,
) -> Union[str, bool, int]:
    """Execute a function powered quality measure on the LLM program output.

    The function signature of the quality measure determines which arguments
    are passed to the function. The list of arguments is truncated to match
    the length of the function signature. Potential arguments in the order
    they are passed to the function are:
        - Output of the LLM program.
        - Test case inputs.
        - Test case itself.
        - quality_measure
    
    Args:
        llm_program_output: Output of the LLM program.
        quality_measure: Quality measure to be executed.
        test_case: Test case on which the LLM program was executed to
            produce llm_program_output.

    Returns:
        Output of the function specified in quality_measure's spec field.
    """
    callable_object = data_model.LazyCallable(quality_measure.spec)
    args = [
        llm_program_output,
        Inputs(test_case.inputs),
        test_case,
        quality_measure,
    ]
    inputs_signature = callable_object.inputs_signature
    quality_measure_output = callable_object(*args[:len(inputs_signature)])
    return quality_measure_output


def _execute_quality_measure_llm(
    llm_program_output: Any,
    quality_measure: data_model.QualityMeasure,
    test_case: data_model.TestCase,
) -> Union[str, bool, int]:
    """Execute a LLM powered quality measure on the LLM program output.

    Args:
        llm_program_output: Output of the LLM program.
        quality_measure: Quality measure.  Must have evaluator field equal
            to "LLM".
        test_case: Test case on which the LLM program was executed to
            produce llm_program_output.
    
    Raises:
        ValueError: If quality measure evaluator is not "LLM".

    Returns:
        Output of the quality measure.
    """
    if quality_measure.evaluator != "LLM":
        raise ValueError("Quality measure evaluator must be 'LLM'.")

    evaluation_type = quality_measure.evaluation_type
    if isinstance(quality_measure.spec, str):
        quality_measure_output = _execute_quality_measure_function(
            llm_program_output, quality_measure, test_case)

    elif isinstance(quality_measure.spec, dict):
        model = quality_measure.spec.get("model", "gpt-3.5-turbo")
        prompt = quality_measure.spec.get("prompt")
        if prompt is None:
            raise ValueError(
                "Quality measure spec must contain a 'prompt' key.")
        quality_measure_output = _openai_llm_quality_measure(
            llm_program_output,
            model=model,
            prompt=prompt,
            inputs=Inputs(test_case.inputs),
            quality_measure=quality_measure,
            test_case=test_case)

    if isinstance(quality_measure_output, str):
        if evaluation_type == "BINARY":
            if quality_measure_output.strip().upper() in ("YES", "Y"):
                quality_measure_output = True
            elif quality_measure_output.strip().upper() in ("NO", "N"):
                quality_measure_output = False

        elif evaluation_type == "RATING_INT":
            quality_measure_output = int(quality_measure_output)

    return quality_measure_output


def execute_quality_measures(
    test_case: data_model.TestCase,
    llm_program_output: Any,
    quality_measure_list: List[data_model.QualityMeasure],
    quality_measure_ids: List[int],
) -> Tuple[List[wire_model.DirectEvaluation], List[Dict[str, Union[
        int, str, wire_model.QualityMeasureExecutionDetails]]]]:
    """Execute quality measures on the LLM program output.

    Execute each executable quality measure in `quality_measure_list`.
    If the result is valid, add it to a list of direct evaluations. If
    the result is invalid, add it to a list of invalid quality measures.
    A quality measure's result is invalid if the quality measure raised an
    error during execution, or if the result does not match the quality
    measure's evaluation type.
 
    Args:
        test_case: Test case on which the LLM program was executed to
            produce llm_program_output.
        llm_program_output: Output of the LLM program.
        quality_measure_list: List of quality measures to be executed.
        quality_measure_ids: IDs of quality measures. The IDs must be in the
            same order as the quality measures in quality_measure_list.
    
    Returns:
        A tuple of the following:
            - List of `wire_model.DirectEvaluation` objects.
            - List of invalid quality measures. Each invalid quality measure
                is a Dictionary with the following keys:
                    "id": ID of quality measure.
                    "name": Name of quality measure.
                    "execution_details":
                        wire_model.QualityMeasureExecutionDetails object.
    """
    direct_evaluations = []
    invalid_quality_measures = []

    if len(quality_measure_list) != len(quality_measure_ids):
        raise ValueError(
            "The number of quality measures and quality measure IDs must be "
            "equal.")

    for quality_measure, quality_measure_id in zip(
        quality_measure_list, quality_measure_ids):
        # Skip quality measures that are not executable.
        if quality_measure.evaluator not in ("FUNCTION", "LLM"):
            continue

        # Run the (executable) quality measure.
        # TODO: https://github.com/inductor-hq/saas/issues/404 - Record
        # quality measure errors, stdout, and stderr on the backend.
        quality_measure_stdout = None
        quality_measure_stderr = None
        quality_measure_error = None
        quality_measure_output = None
        with execution.capture_stdout_stderr(
            suppress=True) as (stdout, stderr):
            try:
                if quality_measure.evaluator == "FUNCTION":
                    quality_measure_output = (
                        _execute_quality_measure_function(
                            llm_program_output,
                            quality_measure,
                            test_case))

                elif quality_measure.evaluator == "LLM":
                    quality_measure_output = (
                        _execute_quality_measure_llm(
                            llm_program_output,
                            quality_measure,
                            test_case))

                else:
                    raise ValueError(
                        "Quality measure evaluator must be 'FUNCTION' or "
                        "'LLM'.")

            except Exception:  # pylint: disable=broad-except
                quality_measure_error = "".join(traceback.format_exc())

            quality_measure_stdout = stdout.getvalue()
            quality_measure_stderr = stderr.getvalue()

        quality_measure_execution_details = (
            wire_model.QualityMeasureExecutionDetails(
                input=llm_program_output,
                output=quality_measure_output,
                error=quality_measure_error,
                stdout=quality_measure_stdout,
                stderr=quality_measure_stderr,
            )
        )

        if quality_measure_error is not None:
            # The result of the quality measure is invalid if the quality
            # measure raised an error during execution.
            invalid_quality_measures.append({
                "id": quality_measure_id,
                "name": quality_measure.name,
                "execution_details": quality_measure_execution_details,
            })
            continue

        # Create direct evaluations for valid quality measure results.
        if quality_measure.evaluation_type == "BINARY" and isinstance(
            quality_measure_output, bool):
            direct_evaluations.append(
                wire_model.DirectEvaluation(
                    quality_measure_id=quality_measure_id,
                    value_bool=quality_measure_output))
        elif (quality_measure.evaluation_type == "RATING_INT" and
                isinstance(quality_measure_output, int) and
                # Required to prevent `bool` from being interpreted as
                # `int`, since `bool` is a subclass of `int`.
                not isinstance(quality_measure_output, bool)):
            direct_evaluations.append(
                wire_model.DirectEvaluation(
                    quality_measure_id=quality_measure_id,
                    value_int=quality_measure_output))
        else:
            # The result of the quality measure is invalid if the result
            # does not match the quality measure's evaluation type.
            expected_output_type = (
                type(True) if quality_measure.evaluation_type == "BINARY"
                else type(5))
            quality_measure_execution_details.error = (
                f"Invalid output type. Expected output type: "
                f"{expected_output_type}. Actual output type: "
                f"{type(quality_measure_output)}")
            invalid_quality_measures.append({
                "id": quality_measure_id,
                "name": quality_measure.name,
                "execution_details": quality_measure_execution_details,
            })

    return direct_evaluations, invalid_quality_measures
