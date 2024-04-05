from dataclasses import dataclass

from atoti_core import get_package_version, keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class WidgetConversionDetails:
    # This class is used in the JupyterLab extension written in JavaScript.
    # JavaScript uses camelCase.
    mdx: str
    sessionId: str  # noqa: N815
    widgetCreationCode: str  # noqa: N815


_MAJOR_VERSION = get_package_version(__name__).split(".", maxsplit=1)[0]

CONVERT_QUERY_RESULT_TO_WIDGET_MIME_TYPE = (
    f"application/vnd.atoti.convert-query-result-to-widget.v{_MAJOR_VERSION}+json"
)
