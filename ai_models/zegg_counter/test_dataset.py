import random
import matplotlib.pyplot as plt

from dataset import EggDataset
from augmentations import get_phase1_transform

# ===========================
# Dataset
# ===========================

dataset = EggDataset(
    image_dir=r"D:\Documents\Codage\Python\Wolbachia_Sicard\test",
    label_dir=r"D:\Documents\Codage\Python\Wolbachia_Sicard\test\Labels",
    transform=get_phase1_transform
)

# ===========================
# Nombre d'images à afficher
# ===========================

N = 6

fig, axes = plt.subplots(
    N,
    4,
    figsize=(18, 4 * N)
)

for i in range(N):

    sample = dataset[random.randint(0, len(dataset)-1)]

    image = sample["image"].permute(1,2,0).numpy()

    heatmap = sample["heatmap"][0].numpy()

    keypoints = sample["keypoints"]

    # -------------------------
    # Image
    # -------------------------

    axes[i,0].imshow(image)
    axes[i,0].set_title(sample["image_name"])
    axes[i,0].axis("off")

    # -------------------------
    # Image + points
    # -------------------------

    axes[i,1].imshow(image)

    if len(keypoints):

        x = [p[0] for p in keypoints]
        y = [p[1] for p in keypoints]

        axes[i,1].scatter(
            x,
            y,
            c="red",
            s=2
        )

    axes[i,1].set_title("Keypoints")
    axes[i,1].axis("off")

    # -------------------------
    # Heatmap
    # -------------------------

    axes[i,2].imshow(
        heatmap,
        cmap="hot"
    )

    axes[i,2].set_title("Heatmap")
    axes[i,2].axis("off")

    # -------------------------
    # Overlay
    # -------------------------

    axes[i,3].imshow(image)

    axes[i,3].imshow(
        heatmap,
        cmap="jet",
        alpha=0.4
    )

    axes[i,3].set_title("Overlay")
    axes[i,3].axis("off")

plt.tight_layout()
plt.show()