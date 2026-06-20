# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:16:04 2026

@author: hugoz
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class Annotation:
    x: int
    y: int
    confidence: float = 1.0


class AnnotationManager:

    MAX_DELETE_DISTANCE = 100

    def __init__(self):

        self.annotations = []
        self.undo_stack = []

    def add_annotation(self, x, y):

        ann = Annotation(x, y)

        self.annotations.append(ann)

        self.undo_stack.append(
            ("add", ann)
        )

    def remove_nearest(self, x0, y0):

        if not self.annotations:
            return False

        distances = [
            np.hypot(
                a.x - x0,
                a.y - y0
            )
            for a in self.annotations
        ]

        idx = int(np.argmin(distances))

        if (
            distances[idx]
            < self.MAX_DELETE_DISTANCE
        ):

            ann = self.annotations.pop(idx)

            self.undo_stack.append(
                ("delete", ann, idx)
            )

            return True

        return False

    def undo(self):

        if not self.undo_stack:
            return

        action = self.undo_stack.pop()

        if action[0] == "add":

            ann = action[1]

            if ann in self.annotations:
                self.annotations.remove(ann)

        elif action[0] == "delete":

            ann = action[1]
            idx = action[2]

            self.annotations.insert(
                idx,
                ann
            )