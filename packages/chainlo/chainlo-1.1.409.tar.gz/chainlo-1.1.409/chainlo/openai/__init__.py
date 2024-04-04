from typing import Union

from chainlo.context import get_context
from chainlo.step import Step
from chainlo.sync import run_sync
from chainlo.utils import check_module_version
from literalai import ChatGeneration, CompletionGeneration
from literalai.helper import timestamp_utc


def instrument_openai():
    if not check_module_version("openai", "1.0.0"):
        raise ValueError(
            "Expected OpenAI version >= 1.0.0. Run `pip install openai --upgrade`"
        )

    from literalai.instrumentation.openai import instrument_openai

    async def on_new_generation(
        generation: Union["ChatGeneration", "CompletionGeneration"], timing
    ):
        context = get_context()

        parent_id = None
        if context.current_step:
            parent_id = context.current_step.id
        elif context.session.root_message:
            parent_id = context.session.root_message.id

        step = Step(
            name=generation.model if generation.model else generation.provider,
            type="llm",
            parent_id=parent_id,
        )
        step.generation = generation
        # Convert start/end time from seconds to milliseconds
        step.start = (
            timestamp_utc(timing.get("start"))
            if timing.get("start", None) is not None
            else None
        )
        step.end = (
            timestamp_utc(timing.get("end"))
            if timing.get("end", None) is not None
            else None
        )

        if isinstance(generation, ChatGeneration):
            step.input = generation.messages
            step.output = generation.message_completion  # type: ignore
        else:
            step.input = generation.prompt
            step.output = generation.completion

        await step.send()

    def on_new_generation_sync(
        generation: Union["ChatGeneration", "CompletionGeneration"], timing
    ):
        run_sync(on_new_generation(generation, timing))

    instrument_openai(None, on_new_generation_sync)
