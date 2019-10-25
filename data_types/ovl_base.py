class OVLBase:
    parent = None
    is_x64 = False

    def register(self, obj: 'OVLBase'):
        obj.parent = self

    @classmethod
    def set_x64_mode(cls, mode):
        cls.is_x64 = mode
