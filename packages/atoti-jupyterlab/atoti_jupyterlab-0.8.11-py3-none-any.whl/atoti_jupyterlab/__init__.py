"""Plugin to create interactive Atoti widgets in JupyterLab.

This package is required to use :attr:`atoti.Session.widget` and :attr:`atoti_query.QuerySession.widget`.
"""


def _jupyter_labextension_paths() -> (  # pyright: ignore[reportUnusedFunction]
    list[dict[str, str]]
):
    """Return the paths used by JupyterLab to load the extension assets."""
    return [{"src": "labextension", "dest": "@atoti/jupyterlab-extension"}]
