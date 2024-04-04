# This file was auto-generated by Fern from our API Definition.

import enum
import typing

T_Result = typing.TypeVar("T_Result")


class EvaluationStatusEnum(str, enum.Enum):
    """
    An enumeration.
    """

    EVALUATION_INITIALIZED = "EVALUATION_INITIALIZED"
    EVALUATION_STARTED = "EVALUATION_STARTED"
    EVALUATION_FINISHED = "EVALUATION_FINISHED"
    EVALUATION_FAILED = "EVALUATION_FAILED"

    def visit(
        self,
        evaluation_initialized: typing.Callable[[], T_Result],
        evaluation_started: typing.Callable[[], T_Result],
        evaluation_finished: typing.Callable[[], T_Result],
        evaluation_failed: typing.Callable[[], T_Result],
    ) -> T_Result:
        if self is EvaluationStatusEnum.EVALUATION_INITIALIZED:
            return evaluation_initialized()
        if self is EvaluationStatusEnum.EVALUATION_STARTED:
            return evaluation_started()
        if self is EvaluationStatusEnum.EVALUATION_FINISHED:
            return evaluation_finished()
        if self is EvaluationStatusEnum.EVALUATION_FAILED:
            return evaluation_failed()
