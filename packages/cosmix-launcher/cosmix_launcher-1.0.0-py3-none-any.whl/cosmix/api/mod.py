from typing import NamedTuple


__all__ = (
    "Mod",
)


class Mod(NamedTuple):
    name: str
    path: str
    version: str
    author: str

    def __repr__(self) -> str:
        s = self.path

        if self.name is not None:
            s += f" [{self.name}]"

        if self.version is not None:
            s += f" ({self.version})"

        return s

    @staticmethod
    def from_data(data: dict, path: str) -> "Mod":
        name = None if "Specification-Name" not in data else data["Specification-Name"]
        version = None if "Specification-Version" not in data else data["Specification-Version"]
        author = None if "Specification-Vendor" not in data else data["Specification-Vendor"]
        return Mod(name, path, version, author)
