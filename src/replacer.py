class FIFOReplacer:

    def __init__(self):
        self.list = list()

    def pin(self, frame_id: int):
        if frame_id in self.list:
            self.list.remove(frame_id)

    def unpin(self, frame_id: int):
        if frame_id not in self.list:
            self.list.append(frame_id)

    def get_victim(self) -> int:
        if self.list:
            return self.list[0]
        return None




