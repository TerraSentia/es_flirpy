import cv2, time
from flirpy.camera.boson_core_edited import Boson
import numpy as np
import struct


def get_temperature(img, top_corner: tuple, bottom_corner: tuple):
    img = img[bottom_corner[0] : top_corner[0], bottom_corner[1] : top_corner[1]]

    crop_row, crop_cols = img.shape
    pixel_value = []
    max = 0
    lowest = 450
    for i in range(0, crop_row):
        for j in range(0, crop_cols):
            value = img[i, j]
            if max < value:
                max = value
            if value < lowest:
                lowest = value
            pixel_value.append(value)
    average_value = np.mean(pixel_value)
    print(
        "Average: ",
        average_value - 273,
        "C max: ",
        max - 273,
        "C lowest: ",
        lowest - 273,
        "C",
    )
    return average_value, max, lowest


with Boson() as camera:
    count = 0
    # set it to radiometric mode
    function_id = 0x000E000D  # sysctrlSetUsbVideoIR16Mode
    command = struct.pack(">H", 2)  # FLR_SYSCTRL_USBIR16_MODE_TLINEAR = 2
    res = camera._send_packet(function_id, data=command)

    # check mode
    function_id = 0x000E000E
    res = camera._send_packet(function_id)
    res = camera._decode_packet(res, receive_size=4)
    print(res)
    camera.find_video_device()

    while True:
        img_original = camera.grab().astype(np.float32)
        img = img_original * 0.01
        avg, max, min = get_temperature(img, (0, 0), (400, 400))
        # print(avg, max, min)

        # Rescale to 8 bits
        img = (
            255
            * (img_original - img_original.min())
            / (img_original.max() - img_original.min())
        )

        # Apply colourmap - try COLORMAP_JET if INFERNO doesn't work.
        # You can also try PLASMA or MAGMA
        img_col = cv2.applyColorMap(img.astype(np.uint8), cv2.COLORMAP_JET)
        filename = str(count) + ".jpeg"
        cv2.imwrite(filename, img_col)
        count = count + 1
        time.sleep(0.1)

