from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class TagType(Enum):
    """
    The span tag types
    """
    Unary = 0
    String = 1
    Number = 2
    Boolean = 3
    Date = 4


@dataclass
class SpanTag:
    """
    Defines a span tag manually to the data contained in the cell path. The tag
    is applied to the subset of data contained between start (inclusive) and end
    (exclusive).

    The cell path describes which cell to apply this tag to. Cell paths can be
    created using the antimatter.cell_path.cell_path(cname, rnum) helper function,
    which takes the name of the column and the row number. As an example, if the
    cell to apply this span tag to was in a column named "name" and was in row 10
    of the data, the cell path would be "name[9]" (the first row would be number 0).
    """
    name: str
    start: Optional[int] = None
    end: Optional[int] = None
    cell_path: str = ""
    tag_type: TagType = TagType.Unary
    tag_value: str = ""


@dataclass
class ColumnTag:
    """
    Defines a column tag manually set to apply a rule to a particular column of data.
    """
    column_name: str
    tag_names: List[str]
    tag_type: TagType = TagType.Unary
    tag_value: str = ""


@dataclass
class CapsuleTag:
    """
    Defines a capsule tag manually set to apply a rule to a capsule.
    """
    name: str
    tag_type: TagType = TagType.Unary
    tag_value: str = ""
