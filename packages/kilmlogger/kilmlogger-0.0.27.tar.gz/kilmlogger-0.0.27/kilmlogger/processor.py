from typing import Any, Sequence

from structlog.typing import WrappedLogger, EventDict


class OrderedDictProcessor:
    def __init__(
        self,
        key_order: Sequence[str] | None = None,
        drop_missing: bool = False,
    ):
        self.key_order = key_order
        self.drop_missing = drop_missing

    def __call__(self, _: WrappedLogger, __: str, event_dict: EventDict) -> str:
        def ordered_items(event_dict: EventDict) -> list[tuple[str, Any]]:
            items = {}
            for key in self.key_order:
                value = event_dict.pop(key, None)
                if value is not None or not self.drop_missing:
                    items.update(
                        {
                            key: value,
                        }
                    )
            return items

        return ordered_items(event_dict)
