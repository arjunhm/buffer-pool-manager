import time

PAGE_SIZE = 5


class CustomByteArray(bytearray):
    def append(self, __item):
        if len(self) > PAGE_SIZE:
            raise ValueError("Exceeding page size")
        super().append(__item)


class Page:
    def __init__(self):
        self.id = None
        self.data = CustomByteArray(PAGE_SIZE)
        self.ref_count = 0
        self.is_dirty = False
        self.last_accessed = 0

    def last_accessed_decorator(func):
        def wrapper(self):
            self.last_accessed = time.time()
            func(self)

        return wrapper

    @last_accessed_decorator
    def incr_ref_count(self):
        self.ref_count += 1

    @last_accessed_decorator
    def decr_ref_count(self):
        if self.ref_count > 0:
            self.ref_count -= 1

    def set_last_accessed(self):
        self.last_accessed = time.time()
