import time


def _get_cur_time():
    return int(time.time())


class _ClientCache:
    """A class to work with specific client's cache."""

    def __init__(self, max_size, ttl, mode):
        self.cache = {}
        self.current_size = 0
        self.max_size = max_size
        self.ttl = ttl
        self.mode = mode

    def _increase_current_size(self):
        self.current_size += 1

    def _reduce_current_size(self):
        self.current_size -= 1

    def _is_cache_full(self):
        return self.current_size == self.max_size

    def _add_info(self, lon, lat, info):
        if self._is_cache_full():
            self._remove_oldest_info()
        cur_time = _get_cur_time()
        self.cache.update({(lon, lat): {"time": cur_time, "info": info}})
        self._increase_current_size()

    def _update_info(self, lon, lat, info):
        cur_time = _get_cur_time()
        del self.cache[lon, lat]
        self.cache[lon, lat] = {"time": cur_time, "info": info}

    def _is_relevant_info(self, lon, lat):
        if self.cache.get((lon, lat)) is None:
            return False
        cur_time = _get_cur_time()
        return self._get_time(lon, lat) + self.ttl >= cur_time

    def _get_oldest_info(self):
        return next(iter(self.cache))

    def _remove_oldest_info(self):
        oldest_info = self._get_oldest_info()
        del self.cache[oldest_info]
        self._reduce_current_size()

    def _get_info(self, lon, lat):
        return self.cache.get((lon, lat))["info"]

    def _get_time(self, lon, lat):
        return self.cache.get((lon, lat))["time"]
