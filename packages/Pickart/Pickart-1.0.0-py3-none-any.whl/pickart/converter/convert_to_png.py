import struct
from io import BytesIO
from pathlib import Path
from typing import Optional

import pygame

from pickart import PickartFile
from pickart.constatnts import strOrPath


def convert_to_png(
    filename: strOrPath, output_dir: strOrPath, output_file_name: Optional[str] = None
):
    """Convert `.pickart` file to `.png`.

    Args:
        filename (strOrPath): `.pickart` file path.
        output_dir (strOrPath): folder where converted file will be saved. If it does not exist it will be created.
        output_file_name (Optional[str]): name for converted file, `.png` extension will be added if needed.

    Raises:
        ValueError: if `.pickart` file is invalid.
    """

    filename = Path(filename)
    output_dir = Path(output_dir)

    if output_file_name is None:
        output_file_name = f"{filename.stem}.png"
    elif not output_file_name.endswith(".png"):
        output_file_name += ".png"

    file = PickartFile(filename)
    if not file.valid:
        raise ValueError(f"'{filename}' invalid Pickart file.")

    buffer = BytesIO()
    palette = file.get_palette()
    pixel_fmt = ">" + "B" * file.fmt.value

    for col in file.get_pixels():
        for colour_index, is_painted in col:
            if colour_index is None:
                buffer.write(struct.pack(pixel_fmt, 0, 0, 0, 0))
                continue

            colour = palette[colour_index]
            colour = colour.colour if is_painted else colour.grayscale
            buffer.write(struct.pack(pixel_fmt, *colour))
    surf = pygame.image.frombuffer(buffer.getbuffer(), file.get_size(), file.fmt.name)  # type: ignore

    output_filename = Path(output_dir, output_file_name)
    pygame.image.save(surf, output_filename)
