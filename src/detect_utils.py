from openalpr import Alpr
from os import environ
import cv2
import os
from src.regular import RegularUtils

_cur_dir = os.path.dirname(os.path.realpath(__file__))
alpr_dir = 'C:/OpenALPR/openalpr_64'
environ['PATH'] = alpr_dir + ';' + environ['PATH']

options_windows = {
    "country": "us",  # "License plate Country"
    "config": alpr_dir + '/openalpr.conf',
    "runtime_data": alpr_dir + '/runtime_data',
}

options_ubuntu = {
    "country": "us",  # "License plate Country"
    "config": os.path.join(_cur_dir, '../conf', "openalpr.ini"),
    "runtime_data": '/usr/share/openalpr/runtime_data',
}

options = options_ubuntu
alpr = Alpr(country=options["country"], config_file=options["config"], runtime_dir=options["runtime_data"])
alpr.is_loaded()
print("\n\t")


def proc(plate_image):

    if False:  # alpr.is_loaded():
        print("Error loading OpenALPR")
    else:
        # print("Using OpenALPR " + alpr.get_version())

        alpr.set_top_n(10)
        alpr.set_default_region("wa")
        alpr.set_detect_region(False)
        jpeg_bytes = open(plate_image, "rb").read()
        results = alpr.recognize_array(jpeg_bytes)

        # Uncomment to see the full results structure
        # import pprint
        # pprint.pprint(results)

        # print("Image size: %dx%d" % (results['img_width'], results['img_height']))
        # print("Processing Time: %f" % results['processing_time_ms'])
        try:
            cleared_plate = RegularUtils(candidates=results['results'][0]['candidates']).determine()
        except Exception as e:
            print(e)
            cleared_plate = ""

        # i = 0
        # for plate in results['results']:
        #     i += 1
        #     print("Plate #%d" % i)
        #     # print("   %12s %12s" % ("Plate", "Confidence"))
        #     for candidate in plate['candidates']:
        #         prefix = "-"
        #         if candidate['matches_template']:
        #             prefix = "*"
        #
        #         print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence']))

        return results, cleared_plate


if __name__ == '__main__':

    # proc(plate_image='../data/DATASET Nigeria ALPR/_MG_2702.JPG')
    proc(plate_image='../data/11.jpg')
