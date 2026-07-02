# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 13:04:05 2026

@author: hugoz
"""

# -*- coding: utf-8 -*-

from pathlib import Path
import random

from config import (
    IMAGE_PATH,
    TEST_IMAGE_PATH,
    TRAIN_SPLIT,
    VAL_SPLIT,
    VAL_RATIO,
    RANDOM_SEED
)


def create_train_val_split():

    random.seed(
        RANDOM_SEED
    )

    all_images = {

        p.name

        for p in Path(
            IMAGE_PATH
        ).iterdir()

        if p.is_file()

    }

    test_images = {

        p.name

        for p in Path(
            TEST_IMAGE_PATH
        ).iterdir()

        if p.is_file()

    }

    available_images = list(

        all_images
        -
        test_images

    )

    random.shuffle(
        available_images
    )

    n_val = int(

        len(available_images)
        *
        VAL_RATIO

    )

    val_images = set(
        available_images[:n_val]
    )

    train_images = set(
        available_images[n_val:]
    )

    assert len(
        train_images & val_images
    ) == 0

    assert len(
        train_images & test_images
    ) == 0

    assert len(
        val_images & test_images
    ) == 0

    Path(
        TRAIN_SPLIT
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        TRAIN_SPLIT,
        "w",
        encoding="utf-8"
    ) as f:

        for name in sorted(
            train_images
        ):

            f.write(
                name + "\n"
            )

    with open(
        VAL_SPLIT,
        "w",
        encoding="utf-8"
    ) as f:

        for name in sorted(
            val_images
        ):

            f.write(
                name + "\n"
            )

    print(
        f"Train : {len(train_images)} images"
    )

    print(
        f"Validation : {len(val_images)} images"
    )

    print(
        f"Test : {len(test_images)} images"
    )