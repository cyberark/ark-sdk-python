from typing import Generic, List, TypeVar

PageItem = TypeVar('PageItem')


class ArkPage(Generic[PageItem]):
    def __init__(self, items: List[PageItem]) -> None:
        self.__items = items

    @property
    def items(self) -> List[PageItem]:
        return self.__items

    def __iter__(self):
        for item in self.__items:
            yield item
