"""Customs JSON Encoders classes."""

from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder


class JSONEncoderDecimalSupport(DjangoJSONEncoder):
    """
    Django JSON Encoder subclass with support Decimal type.
    """

    def default(self, o):
        """Wrap up Decimal type."""

        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)
