# Fixed public trust only; no customer-editable setting can enable collaboration.
from _agrolines_license_settings import ORIGIN

from core.offline_policy import enforce

enforce(native=False, licensing_endpoint=ORIGIN)
