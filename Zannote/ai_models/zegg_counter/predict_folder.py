from pathlib import Path

import cv2

from config import (
    PEAK_THRESHOLD,
    PEAK_MIN_DISTANCE
)

from peak_detection import detect_peaks

from summary_manager import (
    save_zannote_csv,
    update_summary
)


def predict_folder(
    image_dir,
    predictor,
    threshold=PEAK_THRESHOLD,
    min_distance=PEAK_MIN_DISTANCE
):

    image_dir = Path(image_dir)

    image_files = sorted(
        p
        for p in image_dir.iterdir()
        if p.suffix.lower() in (
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tif",
            ".tiff"
        )
    )

    for image_path in image_files:

        print(image_path.name)

        heatmap, scale, left, top = predictor.predict_heatmap(
            image_path
        )

        points = detect_peaks(
            heatmap,
            threshold,
            min_distance
        )

        image = cv2.imread(str(image_path))

        height, width = image.shape[:2]

        csv_path = (
            image_path.parent /
            f"{image_path.stem}.csv"
        )

        save_zannote_csv(
            image_path,
            points,
            image_dir
        )

    update_summary(image_dir)

    print(
        f"Résumé mis à jour : "
        f"{image_dir / (image_dir.name + '.xlsx')}"
    )