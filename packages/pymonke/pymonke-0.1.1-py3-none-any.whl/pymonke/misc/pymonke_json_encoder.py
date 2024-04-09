from json import JSONEncoder
from uncertainties.core import Variable, AffineScalarFunc


class PyMonkeJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Variable, AffineScalarFunc)):
            return str(obj)
        return PyMonkeJSONEncoder.default(self)