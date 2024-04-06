from enum import Enum
from dataclasses import dataclass, field


class Icon(Enum):

    ADD = 'fas fa-plus'
    EDIT = 'fas fa-pencil'
    LIST = 'fas fa-list'
    OPEN_RELATED = 'icon-open-related'
    ENVELOPE = 'fas fa-envelope'
    CLEAR = 'icon-clear'
    BACKSPACE = 'icon-backspace'
    FILTER = 'icon-filter'
    DELETE_FILTER = 'icon-delete-filter'
    SELECT = 'icon-select'


class ActionMethod(Enum):

    HREF = 'href'
    GET = 'hx-get'
    POST = 'hx-post'
    PUT = 'hx-put'
    DELETE = 'hx-delete'


@dataclass
class ClientActionGroup:

    name: str
    actions: list[ActionMethod] = field(default_factory=list)
    icon: Icon | type[Enum] = None
    icon_only: bool = False


@dataclass
class ClientAction:

    name: str
    url: str = ''
    method: ActionMethod = ActionMethod.HREF
    attrs: list[tuple[str, str]] = field(default_factory=list)
    submit: bool = False
    form_id: str = 'form'
    class_list: list[str] = field(default_factory=list)
    icon: Icon | type[Enum] = None
    icon_only: bool = False

    def attrs_str(self):
        return ' '.join([f'{str(attr[0])}={str(attr[1])}' for attr in self.attrs])


class TableFieldAlignment(Enum):

    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'


class TableFieldType(Enum):

    NONE = ''
    STRING = '_string'
    MONETARY = '_monetary'
    FLOAT = '_float'
    CHOICE_DISPLAY = '_choice_display'


@dataclass
class TableField:

    label: str
    name: str
    alignment: TableFieldAlignment | Enum = TableFieldAlignment.LEFT
    header_alignment: TableFieldAlignment | Enum = None
    header_info: str = None
    field_type: TableFieldType | Enum = TableFieldType.NONE
    prefix: str = ''
    suffix: str = ''
    truncate_after: int = 0
    template: str = None
    is_relation: bool = False


@dataclass
class BreadCrumb:

    name: str
    url: str
