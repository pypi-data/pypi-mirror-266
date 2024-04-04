#!/usr/bin/env python3
import rich
import pandas as pd


class SensorThingsDbConnector:
    def __init__(self):
        pass

    def say_hello(self):
        rich.print("[orange1]Hi! I'm a SensorThings Database Connector")

    def dummy_df(self):
        d = {
            "a": [0, 1, 2, 3, 5, 6],
            "b": [4, 7, 2, 5, 7,8]
        }
        return pd.DataFrame(d)