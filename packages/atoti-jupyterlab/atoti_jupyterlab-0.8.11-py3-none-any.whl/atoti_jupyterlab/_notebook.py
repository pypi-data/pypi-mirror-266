from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from atoti_core import get_ipython

from ._notebook_cell import NotebookCell

if TYPE_CHECKING:
    from ipykernel.ipkernel import (  # pylint: disable=undeclared-dependency, nested-import
        IPythonKernel,
    )


class Notebook:
    _current_cell: Optional[NotebookCell] = None
    _running_in_supported_kernel: bool = False

    def __init__(self) -> None:
        ipython = get_ipython()

        if ipython is None:
            return

        kernel = getattr(ipython, "kernel", None)

        if kernel is None or not hasattr(kernel, "comm_manager"):
            # When run from IPython or another less elaborated environment than JupyterLab, these attributes might be missing.
            # In that case, there is no need to register anything.
            return

        self._running_in_supported_kernel = True

        self._wrap_execute_request_handler_to_extract_widget_details(kernel)

    @property
    def current_cell(self) -> Optional[NotebookCell]:
        return self._current_cell

    @property
    def running_in_supported_kernel(self) -> bool:
        return self._running_in_supported_kernel

    def _wrap_execute_request_handler_to_extract_widget_details(
        self,
        kernel: IPythonKernel,
    ) -> None:
        original_handler = kernel.shell_handlers["execute_request"]

        def execute_request(  # pylint: disable=too-many-positional-parameters
            stream: Any, ident: Any, parent: Any
        ) -> Any:
            metadata = parent["metadata"]
            cell_id = metadata.get("cellId")
            self._current_cell = (
                None
                if cell_id is None
                else NotebookCell(
                    has_built_widget=bool(metadata.get("atoti", {}).get("state")),
                    id=cell_id,
                )
            )

            return original_handler(stream, ident, parent)

        kernel.shell_handlers["execute_request"] = execute_request
