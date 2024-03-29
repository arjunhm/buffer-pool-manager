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
        self.free_list = [i for i in range(MAX_FRAMES)]  # TODO Make this StaticArray
        self.page_table = dict()  # d[page_id] = frame_id
        self.replacer = FIFOReplacer()  # Replacement Policy
        self.disk_manager = DiskManager()

    def get_free_frame(self):
        if self.free_list:
            frame_id = self.free_list[0]
            self.free_list = self.free_list[1:]
            return frame_id, False

        # Get frame from replacer
        frame_id = self.replacer.get_victim()
        return frame_id, True

    def fetch_page(self, page_id: int) -> Page:
        # Get frame from page table
        frame_id = self.page_table.get(page_id)
        if frame_id:
            page = self.frames[frame_id]
            page.incr_ref_count()
            self.replacer.pin(frame_id)
            return page

        # Get frame from free list or replacement policy
        frame_id, is_from_free_list = self.get_free_frame()
        if frame_id is None:
            return None

        # If frame fetched from eviction
        if is_from_free_list is False:
            page_tbd = self.frames[frame_id]
            # Flush out page and remove it from frames
            if page_tbd:
                if page_tbd.is_dirty:
                    self.disk_manager.write_page(page_tbd)
                del self.page_table[page_tbd.id]

        # Read page from disk
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

        raise PageNotFoundError()

    def flush_page(self, page_id: int) -> bool:
        frame_id = self.page_table.get(page_id)

        if frame_id:
            page = self.frames[frame_id]

            self.disk_manager.write_page(page)
            page.is_dirty = False

            page.decr_ref_count()
            if page.ref_count <= 0:
                self.replacer.unpin(frame_id)
            return True
        return False

    def flush_all_pages(self):
        for page_id in self.page_table.keys():
            self.flush_page(page_id)

    def new_page(self) -> Page:
        # Get frame from free list or replacement policy
        frame_id, is_from_free_list = self.get_free_frame()
        if frame_id is None:
            return None

        # If frame fetched from eviction
        if is_from_free_list is False:
            page_tbd = self.frames[frame_id]
            # Flush out page and remove from frames
            if page_tbd:
                if page_tbd.is_dirty:
                    self.disk_manager.write_page(page_tbd)
                del self.page_table[page_tbd.id]

        page_id = self.disk_manager.allocate_page()
        page = Page(page_id)

        page.incr_ref_count()
        self.replacer.pin(frame_id)
        self.frames[frame_id] = page
        self.page_table[page_id] = frame_id

        return page

    def delete_page(self, page_id):
        frame_id = self.page_table.get(page_id)
        if frame_id is None:
            return None

        del self.page_table[page_id]
        self.replacer.pin(frame_id)
        self.frames.remove(frame_id)  # ? remove frame from frames??
        self.free_list.append(frame_id)
        self.disk_manager.deallocate_page(page_id)
