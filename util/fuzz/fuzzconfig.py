"""
This module provides a structure to define the fuzz environment
"""


class FuzzConfig:
    def __init__(self, device, tiles):
        """
        :param device: Target device name
        :param tiles: List of tiles to consider during fuzzing
        """
        self.device = device
        self.tiles = tiles
