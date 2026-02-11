from r_framework import LogMixin


class ZsndLogMixin(LogMixin):
    LOGGER_PRFIX = "zsnd."


class ZsndError(Exception):
    pass
