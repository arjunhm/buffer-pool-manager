from src.page import Page

MAX_NUM_PAGES = 15


class DiskManager:
    def __init__(self):
        self.num_pages = -1  # Tracks number of pages
        self.pages = dict()  # pages[page_id] = Page

    def read_page(self, page_id: int) -> Page:
        return self.pages[page_id]

    def write_page(self, page: Page):
        self.pages[page.id] = page
        self.page.is_dirty = False

    def allocate_page(self, page_id: int) -> int:
        if self.num_pages >= MAX_NUM_PAGES:
            raise ValueError("Page limit exceeded")

        self.num_pages += 1
        return self.num_pages

    # FIXME decrement num_pages and fix how pageID is assigned. Too sleepy rn
    def deallocate_page(self, page_id: int):
        del self.pages[page_id]
