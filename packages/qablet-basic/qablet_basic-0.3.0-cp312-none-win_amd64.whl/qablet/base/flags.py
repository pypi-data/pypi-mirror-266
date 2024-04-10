from enum import IntFlag


class Stats(IntFlag):
    PV_VEC = 1
    CHOICES = 2
    PV_GRID = 4
    CASHFLOW = 8
