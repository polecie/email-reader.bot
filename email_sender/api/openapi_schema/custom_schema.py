from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter


class CustomAutoSchema(AutoSchema):
    global_params = [
        OpenApiParameter(
            name="tg-id",
            type=str,
            location=OpenApiParameter.HEADER,
            description="Авторизация действий с пользовательской информацией",
            required=True,
        )
    ]

    def get_override_parameters(self):
        params = super().get_override_parameters()
        return params + self.global_params
