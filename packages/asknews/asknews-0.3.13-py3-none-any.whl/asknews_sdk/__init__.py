# flake8: noqa
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from asknews_sdk.version import __version__
from asknews_sdk.sdk import AskNewsSDK

__all__ = (
    "__version__",
    "AskNewsSDK",
)
