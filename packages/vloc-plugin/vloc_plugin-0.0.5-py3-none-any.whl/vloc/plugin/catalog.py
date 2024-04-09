from vloc.plugin.__info__ import DetectInfo


class action:
    ...

    @classmethod
    def slide_up(start: float = 0.8, end: float = 0.1, duration=0):
        ...

    @classmethod
    def slide_down(start: float = 0.1, end: float = 0.8, duration=0):
        ...

    @classmethod
    def slide_e2e(start: DetectInfo, end: DetectInfo, duration=1000):
        ...


