
def overshoot(t, s=1.70158):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1

