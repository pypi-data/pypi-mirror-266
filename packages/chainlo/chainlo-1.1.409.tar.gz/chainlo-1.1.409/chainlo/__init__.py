import os

from dotenv import load_dotenv

env_found = load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from fastapi import Request, Response
from pydantic.dataclasses import dataclass
from starlette.datastructures import Headers

if TYPE_CHECKING:
    from chainlo.haystack.callbacks import HaystackAgentCallbackHandler
    from chainlo.langchain.callbacks import (
        LangchainCallbackHandler,
        AsyncLangchainCallbackHandler,
    )
    from chainlo.llama_index.callbacks import LlamaIndexCallbackHandler
    from chainlo.openai import instrument_openai

import chainlo.input_widget as input_widget
from chainlo.action import Action
from chainlo.cache import cache
from chainlo.chat_settings import ChatSettings
from chainlo.config import config
from chainlo.context import context
from chainlo.element import (
    Audio,
    Avatar,
    File,
    Image,
    Pdf,
    Plotly,
    Pyplot,
    Task,
    TaskList,
    TaskStatus,
    Text,
    Video,
)
from chainlo.logger import logger
from chainlo.message import (
    AskActionMessage,
    AskFileMessage,
    AskUserMessage,
    ErrorMessage,
    Message,
)
from chainlo.oauth_providers import get_configured_oauth_providers
from chainlo.step import Step, step
from chainlo.sync import make_async, run_sync
from chainlo.telemetry import trace
from chainlo.types import ChatProfile, ThreadDict
from chainlo.user import PersistedUser, User
from chainlo.user_session import user_session
from chainlo.utils import make_module_getattr, wrap_user_function
from chainlo.version import __version__
from literalai import ChatGeneration, CompletionGeneration, GenerationMessage

if env_found:
    logger.info("Loaded .env file")


@trace
def password_auth_callback(func: Callable[[str, str], Optional[User]]) -> Callable:
    """
    Framework agnostic decorator to authenticate the user.

    Args:
        func (Callable[[str, str], Optional[User]]): The authentication callback to execute. Takes the email and password as parameters.

    Example:
        @cl.password_auth_callback
        async def password_auth_callback(username: str, password: str) -> Optional[User]:

    Returns:
        Callable[[str, str], Optional[User]]: The decorated authentication callback.
    """

    config.code.password_auth_callback = wrap_user_function(func)
    return func


@trace
def header_auth_callback(func: Callable[[Headers], Optional[User]]) -> Callable:
    """
    Framework agnostic decorator to authenticate the user via a header

    Args:
        func (Callable[[Headers], Optional[User]]): The authentication callback to execute.

    Example:
        @cl.header_auth_callback
        async def header_auth_callback(headers: Headers) -> Optional[User]:

    Returns:
        Callable[[Headers], Optional[User]]: The decorated authentication callback.
    """

    config.code.header_auth_callback = wrap_user_function(func)
    return func


@trace
def oauth_callback(
    func: Callable[[str, str, Dict[str, str], User], Optional[User]]
) -> Callable:
    """
    Framework agnostic decorator to authenticate the user via oauth

    Args:
        func (Callable[[str, str, Dict[str, str], User], Optional[User]]): The authentication callback to execute.

    Example:
        @cl.oauth_callback
        async def oauth_callback(provider_id: str, token: str, raw_user_data: Dict[str, str], default_app_user: User) -> Optional[User]:

    Returns:
        Callable[[str, str, Dict[str, str], User], Optional[User]]: The decorated authentication callback.
    """

    if len(get_configured_oauth_providers()) == 0:
        raise ValueError(
            "You must set the environment variable for at least one oauth provider to use oauth authentication."
        )

    config.code.oauth_callback = wrap_user_function(func)
    return func


@trace
def on_logout(func: Callable[[Request, Response], Any]) -> Callable:
    """
    Function called when the user logs out.
    Takes the FastAPI request and response as parameters.
    """

    config.code.on_logout = wrap_user_function(func)
    return func


@trace
def on_message(func: Callable) -> Callable:
    """
    Framework agnostic decorator to react to messages coming from the UI.
    The decorated function is called every time a new message is received.

    Args:
        func (Callable[[Message], Any]): The function to be called when a new message is received. Takes a cl.Message.

    Returns:
        Callable[[str], Any]: The decorated on_message function.
    """

    config.code.on_message = wrap_user_function(func)
    return func


@trace
def on_chat_start(func: Callable) -> Callable:
    """
    Hook to react to the user websocket connection event.

    Args:
        func (Callable[], Any]): The connection hook to execute.

    Returns:
        Callable[], Any]: The decorated hook.
    """

    config.code.on_chat_start = wrap_user_function(func, with_task=True)
    return func


@trace
def on_chat_resume(func: Callable[[ThreadDict], Any]) -> Callable:
    """
    Hook to react to resume websocket connection event.

    Args:
        func (Callable[], Any]): The connection hook to execute.

    Returns:
        Callable[], Any]: The decorated hook.
    """

    config.code.on_chat_resume = wrap_user_function(func, with_task=True)
    return func


@trace
def set_chat_profiles(
    func: Callable[[Optional["User"]], List["ChatProfile"]]
) -> Callable:
    """
    Programmatic declaration of the available chat profiles (can depend on the User from the session if authentication is setup).

    Args:
        func (Callable[[Optional["User"]], List["ChatProfile"]]): The function declaring the chat profiles.

    Returns:
        Callable[[Optional["User"]], List["ChatProfile"]]: The decorated function.
    """

    config.code.set_chat_profiles = wrap_user_function(func)
    return func


@trace
def on_chat_end(func: Callable) -> Callable:
    """
    Hook to react to the user websocket disconnect event.

    Args:
        func (Callable[], Any]): The disconnect hook to execute.

    Returns:
        Callable[], Any]: The decorated hook.
    """

    config.code.on_chat_end = wrap_user_function(func, with_task=True)
    return func


@trace
def author_rename(func: Callable[[str], str]) -> Callable[[str], str]:
    """
    Useful to rename the author of message to display more friendly author names in the UI.
    Args:
        func (Callable[[str], str]): The function to be called to rename an author. Takes the original author name as parameter.

    Returns:
        Callable[[Any, str], Any]: The decorated function.
    """

    config.code.author_rename = wrap_user_function(func)
    return func


@trace
def on_stop(func: Callable) -> Callable:
    """
    Hook to react to the user stopping a thread.

    Args:
        func (Callable[[], Any]): The stop hook to execute.

    Returns:
        Callable[[], Any]: The decorated stop hook.
    """

    config.code.on_stop = wrap_user_function(func)
    return func


def action_callback(name: str) -> Callable:
    """
    Callback to call when an action is clicked in the UI.

    Args:
        func (Callable[[Action], Any]): The action callback to execute. First parameter is the action.
    """

    def decorator(func: Callable[[Action], Any]):
        config.code.action_callbacks[name] = wrap_user_function(func, with_task=True)
        return func

    return decorator


def on_settings_update(
    func: Callable[[Dict[str, Any]], Any]
) -> Callable[[Dict[str, Any]], Any]:
    """
    Hook to react to the user changing any settings.

    Args:
        func (Callable[], Any]): The hook to execute after settings were changed.

    Returns:
        Callable[], Any]: The decorated hook.
    """

    config.code.on_settings_update = wrap_user_function(func, with_task=True)
    return func


def sleep(duration: int):
    """
    Sleep for a given duration.
    Args:
        duration (int): The duration in seconds.
    """
    return asyncio.sleep(duration)


@dataclass()
class CopilotFunction:
    name: str
    args: Dict[str, Any]

    def acall(self):
        return context.emitter.send_call_fn(self.name, self.args)


__getattr__ = make_module_getattr(
    {
        "LangchainCallbackHandler": "chainlo.langchain.callbacks",
        "AsyncLangchainCallbackHandler": "chainlo.langchain.callbacks",
        "LlamaIndexCallbackHandler": "chainlo.llama_index.callbacks",
        "HaystackAgentCallbackHandler": "chainlo.haystack.callbacks",
        "instrument_openai": "chainlo.openai",
    }
)

__all__ = [
    "user_session",
    "CopilotFunction",
    "Action",
    "User",
    "PersistedUser",
    "Audio",
    "Pdf",
    "Plotly",
    "Image",
    "Text",
    "Avatar",
    "Pyplot",
    "File",
    "Task",
    "TaskList",
    "TaskStatus",
    "Video",
    "ChatSettings",
    "input_widget",
    "Message",
    "ErrorMessage",
    "AskUserMessage",
    "AskActionMessage",
    "AskFileMessage",
    "Step",
    "step",
    "ChatGeneration",
    "CompletionGeneration",
    "GenerationMessage",
    "on_logout",
    "on_chat_start",
    "on_chat_end",
    "on_chat_resume",
    "on_stop",
    "action_callback",
    "author_rename",
    "on_settings_update",
    "password_auth_callback",
    "header_auth_callback",
    "sleep",
    "run_sync",
    "make_async",
    "cache",
    "context",
    "LangchainCallbackHandler",
    "AsyncLangchainCallbackHandler",
    "LlamaIndexCallbackHandler",
    "HaystackAgentCallbackHandler",
    "instrument_openai",
]


def __dir__():
    return __all__
