# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:16:54 2026

@author: hugoz
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

class CsvManager:

    def __init__(self, label_folder, image_folder):

        self.label_folder = label_folder
        self.image_folder = image_folder

        os.makedirs(
            label_folder,
            exist_ok=True
        )

    def get_csv_path(
        self,
        image_name
    ):

        return os.path.join(
            self.label_folder,
            f"{image_name}.csv"
        )

    def load_annotations(
        self,
        image_name
    ):

        path = self.get_csv_path(
            image_name
        )

        if not os.path.exists(path):
            return []

        try:

            df = pd.read_csv(path)

            return list(
                zip(
                    df["x"],
                    df["y"]
                )
            )

        except Exception as e:

            print(e)

            return []

    def save_annotations(
        self,
        image_name,
        width,
        height,
        annotations
    ):

        df = pd.DataFrame({

            "image":
                [image_name]
                * len(annotations),

            "width":
                [width]
                * len(annotations),

            "height":
                [height]
                * len(annotations),

            "egg_id":
                range(
                    1,
                    len(annotations)+1
                ),

            "x":
                [a.x for a in annotations],

            "y":
                [a.y for a in annotations],

            "confidence":
                [a.confidence
                 for a in annotations]

        })

        df.to_csv(
            self.get_csv_path(
                image_name
            ),
            index=False
        )
        self.update_summary()
        
    def update_summary(self):
    
        rows = []
    
        for csv_file in sorted(Path(self.label_folder).glob("*.csv")):
    
            df = pd.read_csv(csv_file)
            
            if df.empty:
                rows.append({
                    "image": csv_file.stem,
                    "egg_count": 0,
                    "mean_probability": np.nan,
                    "std_probability": np.nan
                })
                continue
            
            rows.append({
    
                "image": csv_file.stem,    
                
                "egg_count": len(df),
    
                "mean_probability": df["confidence"].mean(),
    
                "std_probability": df["confidence"].std(ddof=0)
    
            })
    
        summary = pd.DataFrame(rows)
    
        output = Path(self.image_folder) / "Summary.xlsx"
    
        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:
    
            summary.to_excel(
                writer,
                index=False
            )
    
            worksheet = writer.sheets["Sheet1"]
    
            for column in worksheet.columns:
    
                length = max(
    
                    len(str(cell.value))
                    if cell.value is not None
                    else 0
    
                    for cell in column
    
                )
    
                worksheet.column_dimensions[
                    column[0].column_letter
                ].width = length + 4