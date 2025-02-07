class UniqueList:
    def __init__(self):
        self.items = []
    
    def append(self, value):
        if value not in self.items:
            self.items.append(value)
    
    def __repr__(self):
        return repr(self.items)
    def __len__(self):
        return len(self.items)
    
    def __contains__(self, value):
        return value in self.items
    
    def __iter__(self):
        return iter(self.items)
    