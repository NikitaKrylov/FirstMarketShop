from .models import *

CT_MODEL_CLASS = {
    'shoes': Shoes,
    'accessory': Accessory,
    'garment': Garment
}

BAD_NAME_SIMBOL = '@#$^&*~;:?№"|'


def get_product_models():
    dict = {}

    for _class in AbstractProduct.__subclasses__():
        dict[_class._meta.model_name] = _class

    return dict

