from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from atoti_core import TEXT_MIME_TYPE, BaseSessionBound, keyword_only_dataclass
from typing_extensions import override

from ._comm_targets import WIDGET_COMM_TARGET_NAME
from ._mime_types import WIDGET_MIME_TYPE
from ._notebook_cell import NotebookCell


@keyword_only_dataclass
@dataclass(frozen=True)
class Widget:
    cell: Optional[NotebookCell]
    running_in_supported_kernel: bool
    session: BaseSessionBound

    def _ipython_display_(self) -> None:
        if not self.running_in_supported_kernel:
            print(self)  # noqa: T201
            return

        from ipykernel.comm import (  # pylint: disable=undeclared-dependency, nested-import
            Comm,
        )
        from IPython.display import (  # pylint: disable=undeclared-dependency, nested-import
            publish_display_data,
        )

        data: dict[str, object] = {
            TEXT_MIME_TYPE: f"""Open the notebook in JupyterLab with the Atoti JupyterLab extension enabled to {"see" if self.cell and self.cell.has_built_widget else "build"} this widget."""
        }

        widget_creation_code = self.session._get_widget_creation_code()

        if widget_creation_code:
            data[WIDGET_MIME_TYPE] = {
                "sessionId": self.session._id,
                "sessionLocation": self.session._location,
                "widgetCreationCode": widget_creation_code,
            }

        # Mypy cannot find the type of this function.
        publish_display_data(data)  # type: ignore[no-untyped-call]

        if self.cell is None:
            return

        widget_id = str(uuid4())

        # Mypy cannot find the type of this class.
        Comm(  # type: ignore[no-untyped-call]
            WIDGET_COMM_TARGET_NAME,
            # The data below is either sensitive (e.g. auth headers) or change from one cell run to the other.
            # It is better to not send it through publish_display_data so that it does not end up in the .ipynb file.
            data={
                "cellId": self.cell.id,
                "sessionHeaders": self.session._generate_auth_headers(),
                "widgetId": widget_id,
            },
        ).close()

        self.session._block_until_widget_loaded(widget_id)

    @override
    def __repr__(self) -> str:
        return "Atoti widgets can only be shown in JupyterLab with the Atoti JupyterLab extension enabled."
