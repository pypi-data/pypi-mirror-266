from abc import ABC, abstractmethod
from enum import Enum
from io import UnsupportedOperation
from typing import Optional


class OpenAPIType(ABC):
    description: str | None = None
    nullable: bool = False

    def __init__(self, description: str | None = None, nullable: bool = False) -> None:
        self.description = description
        self.nullable = nullable

    @abstractmethod
    def asdict(self) -> dict[str, object]:
        pass

    def asarguments(self) -> dict[str, dict[str, object]]:
        raise UnsupportedOperation

    def add_addl_info(self, emitted: dict[str, object]) -> dict[str, object]:
        if self.description is not None:
            emitted["description"] = self.description
        if self.nullable:
            emitted["nullable"] = self.nullable
        return emitted


class OpenAPIRefType(OpenAPIType):
    source: str

    def __init__(
        self, source: str, description: str | None = None, nullable: bool = False
    ) -> None:
        self.source = source
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {"$ref": self.source}


class OpenAPIPrimitive(str, Enum):
    string = "string"
    boolean = "boolean"
    integer = "integer"
    number = "number"


class OpenAPIPrimitiveType(OpenAPIType):
    base_type: OpenAPIPrimitive

    def __init__(
        self,
        base_type: OpenAPIPrimitive,
        description: str | None = None,
        nullable: bool = False,
    ) -> None:
        self.base_type = base_type
        super().__init__(description=description, nullable=nullable)

    @property
    def value(self) -> str:
        return self.base_type.value

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {"type": self.value}


def OpenAPIStringT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.string)


def OpenAPIBooleanT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.boolean)


def OpenAPIIntegerT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.integer)


def OpenAPINumberT() -> OpenAPIPrimitiveType:
    return OpenAPIPrimitiveType(base_type=OpenAPIPrimitive.number)


class OpenAPIEmptyType(OpenAPIType):
    def __init__(self, description: str | None = None, nullable: bool = False) -> None:
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({})


class OpenAPIEnumType(OpenAPIType):
    """
    represents OpenAPIs type: "string"; with enum set to the corresponding
    options
    """

    base_type: OpenAPIPrimitiveType = OpenAPIStringT()
    options: list[str]

    def __init__(
        self, options: list[str], description: str | None = None, nullable: bool = False
    ) -> None:
        self.options = options
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({
            "type": self.base_type.value,
            "enum": self.options,
        })


class OpenAPIArrayType(OpenAPIType):
    """
    represents OpenAPIs type: "array"
    """

    base_types: list[OpenAPIType]

    def __init__(
        self,
        base_types: OpenAPIType | list[OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
    ) -> None:
        if not isinstance(base_types, list):
            base_types = [base_types]
        self.base_types = base_types
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        items = [base_type.asdict() for base_type in self.base_types]
        return self.add_addl_info({
            "type": "array",
            "items": items[0] if len(items) == 1 else items,
        })


class OpenAPIFreeFormObjectType(OpenAPIType):
    def __init__(self, description: str | None = None, nullable: bool = False) -> None:
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({"type": "object"})

    def asarguments(self) -> dict[str, dict[str, object]]:
        return {}


class OpenAPIObjectType(OpenAPIType):
    """
    represents OpenAPIs type: "object"
    """

    properties: dict[str, OpenAPIType]

    def __init__(
        self,
        properties: dict[str, OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
        *,
        property_desc: Optional[dict[str, str]] = None,
    ) -> None:
        self.properties = properties
        if property_desc is None:
            self.property_desc = {}
        else:
            self.property_desc = property_desc
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        return self.add_addl_info({
            "type": "object",
            "properties": {
                property_name: {
                    **property_type.asdict(),
                    "description": self.property_desc.get(property_name),
                }
                for property_name, property_type in self.properties.items()
            },
        })

    def asarguments(self) -> dict[str, dict[str, object]]:
        argument_types: dict[str, dict[str, object]] = {}
        for property_name, property_type in self.properties.items():
            desc = self.property_desc.get(property_name)
            argument_types[property_name] = {
                "name": property_name,
                "in": "query",
                "schema": property_type.asdict(),
                "required": not property_type.nullable,
                "description": desc or "",
            }
        return argument_types


class OpenAPIUnionType(OpenAPIType):
    """
    represents OpenAPIs type: "oneOf"
    """

    base_types: list[OpenAPIType]

    def __init__(
        self,
        base_types: list[OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
    ) -> None:
        self.base_types = base_types
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {"oneOf": [base_type.asdict() for base_type in self.base_types]}

    def asarguments(self) -> dict[str, dict[str, object]]:
        # TODO handle inheritence (allOf and refs); need to inline here...
        # for now skip this endpoint

        return {}


class OpenAPIIntersectionType(OpenAPIType):
    """
    represents OpenAPIs type: "allOf"
    """

    base_types: list[OpenAPIType]

    def __init__(
        self,
        base_types: list[OpenAPIType],
        description: str | None = None,
        nullable: bool = False,
    ) -> None:
        self.base_types = base_types
        super().__init__(description=description, nullable=nullable)

    def asdict(self) -> dict[str, object]:
        # TODO: use parents description and nullable
        return {"allOf": [base_type.asdict() for base_type in self.base_types]}

    def asarguments(self) -> dict[str, dict[str, object]]:
        # TODO handle inheritence (allOf and refs); need to inline here...
        # for now skip this endpoint

        return {}
