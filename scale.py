class LinearScale:
    def __init__(self, domain_min, domain_max, range_min, range_max):
        self.domain_min = domain_min
        self.domain_max = domain_max
        self.range_min = range_min
        self.range_max = range_max
        self.domain_span = domain_max - domain_min
        self.range_span = range_max - range_min

    def __call__(self, value):
        scale = (value - self.domain_min) / self.domain_span
        return self.range_min + scale * self.range_span

    def clamp(self, value):
        return max(min(value, self.domain_max), self.domain_min)


    def scale(self, value):
        scale = self.range_span / self.domain_span
        return scale*value

