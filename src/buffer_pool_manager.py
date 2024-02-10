from disk_manager import DiskManager
from replacer import FIFOReplacer
from page import Page
from exceptions import PageNotFoundError

MAX_FRAMES = 5


class StaticArray(list):
    def append(self, __object):
        if len(self) > MAX_FRAMES:
            raise ValueError("Exceeding limit")

        super().append(__object)


class BufferPoolManager:
    def __init__(self):
        self.frames = StaticArray(MAX_FRAMES)
        self.free_list = [i for i in range(MAX_FRAMES)]
        self.page_table = dict()  # d[page_id] = frame_id
        self.replacer = FIFOReplacer()  # Replacement Policy
        self.disk_manager = DiskManager()

    def get_free_frame(self):
        if self.free_list:
            frame_id = self.free_list[0]
            self.free_list = self.free_list[1:]
            return frame_id, False

        frame_id = self.replacer.get_victim()
        return frame_id, True

    def fetch_page(self, page_id: int) -> Page:
        frame_id = self.page_table.get(page_id)
        if frame_id:
            page = self.frames[frame_id]
            page.incr_ref_count()
            self.replacer.pin(frame_id)
            return page

        frame_id, is_from_free_list = self.get_free_frame()

        if frame_id is None:
            return None

        if not is_from_free_list:
            page_tbd = self.frames[frame_id]
            if page_tbd.is_dirty:
                self.disk_manager.write_page(page_tbd)
            del self.page_table[page_tbd.id]

        page = self.disk_manager.read_page(page_id)

        self.frames[frame_id] = page
        self.page_table[page_id] = frame_id

        page.incr_ref_count()
        self.replacer.pin(frame_id)

        return page

    def unpin_page(self, page_id, is_dirty):
        frame_id = self.page_table.get(page_id)

        if frame_id:
            page = self.frames[frame_id]
            page.decr_ref_count()

            if page.ref_count <= 0:
                self.replacer.unpin(frame_id)

            return

        raise PageNotFoundError()

    def flush_page(self, page_id: int) -> bool:
        frame_id = self.page_table.get(page_id)

        if frame_id:
            page = self.frames[frame_id]
            page.decr_ref_count()
            self.disk_manager.write_page(page)

            if page.ref_count <= 0:
                self.replacer.unpin(frame_id)
            page.is_dirty = False
            return True

        return False
