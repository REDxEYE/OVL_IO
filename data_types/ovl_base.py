class OVLBase:
    parent = None

    def register(self, obj: 'OVLBase'):
        obj.parent = self
