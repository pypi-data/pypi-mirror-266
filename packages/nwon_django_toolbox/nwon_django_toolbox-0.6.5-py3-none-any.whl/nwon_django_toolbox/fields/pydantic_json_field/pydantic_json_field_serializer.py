import copy
from typing import List, Optional, Type

from jsonschema_to_openapi.convert import convert as convert_to_openapi
from nwon_baseline.pydantic import pydantic_model_to_dict, schema_from_pydantic_model
from nwon_baseline.typings import AnyDict
from pydantic import ValidationError as PydanticValidationError
from pydantic.main import BaseModel
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.serializers import JSONField

__all__ = ["PydanticJsonFieldSerializer"]


class PydanticJsonFieldSerializer(JSONField):
    """
    Serializer for serializing our custom PydanticJsonField.

    Provides annotations for both drf-spectacular and drf-yasg
    """

    class Meta:
        swagger_schema_fields: AnyDict

    def __init__(
        self, *args, pydantic_models: Optional[List[Type[BaseModel]]] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.schema = self.__schema_information(pydantic_models)

        # Set schema for drf-spectacular
        self.coreapi_schema = convert_to_openapi(copy.deepcopy(self.schema))

        # Set schema for drf-yasg
        PydanticJsonFieldSerializer.Meta.swagger_schema_fields = self.schema

        self.pydantic_models = pydantic_models if pydantic_models else []

    def to_representation(self, value):
        value = super().to_representation(value)

        for model in self.pydantic_models:
            try:
                if isinstance(value, dict):
                    return pydantic_model_to_dict(model.model_validate(value))
                else:
                    return pydantic_model_to_dict(model.model_validate_strings(value))
            except PydanticValidationError:
                pass

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        for model in self.pydantic_models:
            try:
                parsed_json = model.model_validate(data)
                return parsed_json.model_dump()
            except PydanticValidationError as error:
                error_details: List[ErrorDetail] = []
                for e in error.errors():
                    error_details.append(ErrorDetail(str(e["loc"]), code=e["msg"]))

                raise ValidationError(error_details) from error

    def __schema_information(
        self, pydantic_models: Optional[List[Type[BaseModel]]]
    ) -> dict:
        """
        Returns a JSON schema that is used for representing the potential values of this field
        """

        if pydantic_models is None or len(pydantic_models) == 0:
            schema_information = {"type": "object"}

        elif len(pydantic_models) > 1:
            schema_information = {
                "anyOf": [
                    schema_from_pydantic_model(model) for model in pydantic_models
                ]
            }
        else:
            schema_information = schema_from_pydantic_model(pydantic_models[0])

        return schema_information


try:
    from drf_spectacular.extensions import OpenApiSerializerFieldExtension

    class PydanticJsonFieldSerializerExtension(OpenApiSerializerFieldExtension):
        target_class = PydanticJsonFieldSerializer

        def map_serializer_field(self, auto_schema, direction):
            return self.target.schema or {"type": "object"}

except Exception:
    pass
