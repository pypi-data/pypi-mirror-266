
class NotifyListener:
    def __init__(self):
        self.listeners = []
    
    def register_listener(self, new_listener):
        self.listeners.append(new_listener)
    
    def notify_listeners(self):
        for item in self.listeners:
            item()
    
    