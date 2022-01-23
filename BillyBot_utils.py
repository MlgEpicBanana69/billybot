import threading
import datetime
import numpy as np
import asyncio

# https://en.wikipedia.org/wiki/Alpha_compositing
def merge_pixels(foreground, background):
    """Merges the values of two pixels to create a new one"""
    foreground_alpha = foreground[3] / 255
    background_alpha = background[3] / 255

    if foreground_alpha == 0.0:
        return background
    elif foreground_alpha == 1.0:
        return foreground

    merged_alpha = (foreground_alpha + background_alpha * (1 - foreground_alpha))

    foreground_red = foreground[0] / 255
    foreground_green = foreground[1] / 255
    foreground_blue = foreground[2] / 255

    background_red = background[0] / 255
    background_green = background[1] / 255
    background_blue = background[2] / 255

    merged_red   = (foreground_red * foreground_alpha+ background_red
                    * background_alpha * (1 - foreground_alpha)) / merged_alpha
    merged_green = (foreground_green * foreground_alpha + background_green
                    * background_alpha * (1 - foreground_alpha)) / merged_alpha
    merged_blue  = (foreground_blue * foreground_alpha + background_blue
                    * background_alpha * (1 - foreground_alpha)) / merged_alpha
    return np.array([int(merged_red * 255), int(merged_green * 255),
                     int(merged_blue * 255), int(merged_alpha * 255)])
