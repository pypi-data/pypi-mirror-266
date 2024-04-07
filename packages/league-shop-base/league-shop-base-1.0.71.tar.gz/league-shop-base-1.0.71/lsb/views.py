from django.conf import settings
from django.utils.module_loading import import_string

# Skin ignore list when getting top sold skins
blacklisted_skins = [
    21002,
    126024,
    222037,
    51028,
    254029,
]


def get_top_sold_skin_values():
    """
    Parse top sold skin value from provided setting
    """
    lsb_setting = getattr(settings, "LSB_SETTINGS", {})
    top_sold_skin_values_settings = lsb_setting.get("top_sold_skin_values")
    if top_sold_skin_values_settings is None:
        return {}

    func_string = top_sold_skin_values_settings.get("func")
    func = import_string(func_string)
    return func(
        *top_sold_skin_values_settings.get("args", []),
        **top_sold_skin_values_settings.get("kwargs", {}),
    )
