# Runs before other frozen runtime hooks and before Qt/GIS initialization.
from core.offline_policy import enforce

enforce(native=False)
