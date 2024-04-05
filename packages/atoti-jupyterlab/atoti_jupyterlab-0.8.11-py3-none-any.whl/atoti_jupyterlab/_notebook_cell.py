from dataclasses import dataclass

from atoti_core import keyword_only_dataclass


@keyword_only_dataclass
@dataclass(frozen=True)
class NotebookCell:
    has_built_widget: bool
    id: str
