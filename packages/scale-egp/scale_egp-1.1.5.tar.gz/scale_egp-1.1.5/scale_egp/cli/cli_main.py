import logging
import sys
from typing import List, Optional
from argh import ArghParser
from scale_egp.cli.collections import (
    CollectionCRUDCommandsForImmutable,
    EGPClientFactory,
    FineTuningJobCommands,
    ModelDeploymentCommands,
    ModelInstanceCommands,
    ModelTemplateCommands,
    TrainingDatasetCommands,
    UserCommands,
    ModelGroupCommands,
)
from scale_egp.cli.formatter import AVAILABLE_FORMATTERS
from scale_egp.cli.parser import get_parser, dispatch
import itertools
from asyncio import iscoroutinefunction, run
from functools import wraps
import traceback


def async_to_sync(fn):
    if iscoroutinefunction(fn):

        @wraps(fn)
        def fn2(self, *args, **kwargs):
            # Note: not passing in self, since the function will be bound to that instance
            return run(fn(*args, **kwargs))

        # bind fn2 to the object to which fn was bound
        # this is important because the class instance is used by formatter to get the
        # title of the output table
        instance = fn.__self__
        bound_method = fn2.__get__(instance, instance.__class__)
        return bound_method
    return fn


def add_commands_to_parser(parser: ArghParser, commands: CollectionCRUDCommandsForImmutable):
    parser.add_commands(
        [
            async_to_sync(getattr(commands, key))
            for key in dir(commands)
            if not key.startswith("_") and callable(getattr(commands, key))
        ],
        group_name=commands.command_group_name,
        group_kwargs={
            "title": getattr(commands, "command_group_title", None),
            "help": getattr(commands, "__doc__", None),
        },
    )


def load_plugins(parser: ArghParser):
    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points
    plugin_commands: List[CollectionCRUDCommandsForImmutable] = []
    for entrypoint in entry_points(group="scale_egp_cli"):
        try:
            plugin_commands.append((entrypoint.load())())
        except Exception as e:
            print(f"Error loading plugin: {str(e)}")
            traceback.print_exception(e)
    return itertools.chain.from_iterable(plugin_commands)


def exec_cli(argv: Optional[List[str]] = None):
    if argv is None:
        argv = sys.argv[1:]
    client_factory = EGPClientFactory()

    parser = get_parser()
    parser.add_argument("--log-curl-commands", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("-k", "--api-key", type=str, default=None, metavar="EGP_API_KEY")
    parser.add_argument(
        "-i",
        "--account-id",
        type=str,
        default=None,
        help="Optional SGP account_id to use. The default account_id will be used if not set.",
        metavar="EGP_ACCOUNT_ID",
    )
    parser.add_argument("-e", "--endpoint-url", type=str, default=None, metavar="EGP_ENDPOINT_URL")
    parser.add_argument(
        "-f", "--format", type=str, choices=[*AVAILABLE_FORMATTERS.keys()], default="rich"
    )
    add_commands_to_parser(parser, ModelGroupCommands(client_factory))
    add_commands_to_parser(parser, ModelInstanceCommands(client_factory))
    add_commands_to_parser(parser, ModelDeploymentCommands(client_factory))
    add_commands_to_parser(parser, ModelTemplateCommands(client_factory))
    add_commands_to_parser(parser, UserCommands(client_factory))
    add_commands_to_parser(parser, FineTuningJobCommands(client_factory))
    add_commands_to_parser(parser, TrainingDatasetCommands(client_factory))
    for plugin_command_cls in load_plugins(parser):
        add_commands_to_parser(parser, plugin_command_cls(client_factory))
    args = parser.parse_args(argv)
    try:
        client_factory.set_client_kwargs(
            api_key=args.api_key,
            endpoint_url=args.endpoint_url,
            account_id=args.account_id,
            log_curl_commands=args.log_curl_commands,
        )
        if args.log_curl_commands:
            logging.basicConfig(level=logging.INFO)
        return dispatch(parser, args, argv=argv)
    except Exception as e:
        if args.verbose:
            traceback.print_exception(e)
        message = getattr(e, "message", None)
        if message is None:
            message = str(e)
        status_code = ""
        if hasattr(e, "code"):
            status_code = f" (HTTP {e.code})"
        print(f"ERROR{status_code}: {message}")
        sys.exit(1)
