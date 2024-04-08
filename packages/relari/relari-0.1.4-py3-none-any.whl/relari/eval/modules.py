from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Type, Union, Iterable
from relari.eval.utils import type_hint_to_str
from relari.eval.dataset import DatasetField

InputType = Union[DatasetField, "Module"]

def _serialize_input_type(obj):
    if isinstance(obj, DatasetField):
        return {"__class__":obj.__class__.__name__, "name": obj.name}
    elif isinstance(obj, Module):
        return  {"__class__":obj.__class__.__name__, "name": obj.name}
    elif isinstance(obj, type):
        return type_hint_to_str(obj)
    elif isinstance(obj, (list, tuple)):
        return [serialize_input_type(x) for x in obj]
    else:
        raise TypeError(f"Object of type {type(obj).__name__} is not serializable")

@dataclass(frozen=True, eq=True)
class Module:
    name: str
    input: Union[Iterable[InputType], InputType, None]
    output: Type
    description: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.name == "":
            raise ValueError(f"Module name cannot be empty")

    def asdict(self):
        return {
            "name": self.name,
            "input": _serialize_input_type(self.input),
            "output": type_hint_to_str(self.output),
            "description": self.description,
        }


@dataclass(frozen=True, eq=True)
class Tool:
    name: str
    args: Dict[str, Type]
    out_type: Type
    description: Optional[str] = field(default=None)

    def asdict(self):
        return asdict(self)


@dataclass(frozen=True, eq=True)
class AgentModule(Module):
    tools: Optional[List[Tool]] = field(default=None)

    def asdict(self):
        return asdict(self)
