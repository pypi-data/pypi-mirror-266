class WithLabel:

    def __init__(self, label: str = None, **kwargs) -> None:
        super(WithLabel, self).__init__(**kwargs)
        self.label = label