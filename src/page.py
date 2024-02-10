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

    def incr_ref_count(self):
        self.ref_count += 1

    def decr_ref_count(self):
        if self.ref_count > 0:
            self.ref_count -= 1
