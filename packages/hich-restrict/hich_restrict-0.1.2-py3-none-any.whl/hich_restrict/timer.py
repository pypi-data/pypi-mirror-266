import time

class Timer:
    def __init__(self):
        self.starttime = None
        self.duration = 0

    def start(self):
        self.starttime = time.perf_counter()
    
    def stop(self):
        end = time.perf_counter()
        if self.starttime is not None:
            self.duration += end-self.starttime
        self.starttime = None
    
    def elapsed(self):
        return time.perf_counter() - self.starttime if self.starttime is not None else 0
    
    def __str__(self):
        return f"Duration (s): {self.duration}"

class MultiTimer:
    def __init__(self, labels):
        self.timers = {}
        for label in labels:
            self.make(label)
    
    def make(self, label):
        self.timers[label] = Timer()

    def start(self, label):
        self.timers[label].start()
    
    def stop(self, label = None):
        if label is None:
            [self.timers[label].stop() for label in self.timers.keys()]
        else:
            self.timers[label].stop()
    
    def __str__(self):
        result = []
        total = sum([timer.duration for timer in self.timers.values()])
        for label, timer in self.timers.items():
            result.append(f"{label} {str(timer)} {round(timer.duration/total*100, 2)}%")
        return '\n'.join(result)
