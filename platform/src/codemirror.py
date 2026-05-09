# https://raw.githubusercontent.com/volltin/nicegui-codemirror/main/codemirror.py
from typing import Callable, Optional

from nicegui.element import Element
from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.elements.mixins.value_element import ValueElement
from nicegui.events import GenericEventArguments


class CodeMirror(ValueElement, DisableableElement, component="codemirror.js"):
    VALUE_PROP = "value"
    LOOPBACK = False

    def __init__(
        self,
        value: str = "",
        on_change: Optional[Callable] = None,
        mode: str = "python",
    ) -> None:
        super().__init__(value=value, on_value_change=on_change)
        self._props["mode"] = mode

    def update(self) -> None:
        super().update()
        self.run_method("update")

    def _event_args_to_value(self, e: GenericEventArguments) -> str:
        return e.args["value"]
