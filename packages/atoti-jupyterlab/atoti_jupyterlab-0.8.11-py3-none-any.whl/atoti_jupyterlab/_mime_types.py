# Keep this file in sync with mimeType.ts.

from atoti_core import get_package_version

_MAJOR_VERSION = get_package_version(__name__).split(".", maxsplit=1)[0]

WIDGET_MIME_TYPE = f"application/vnd.atoti.widget.v{_MAJOR_VERSION}+json"
