import logging
import time

import cv2
import imutils
import numpy as np
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import CompressedImage

import cli_args  as cli
import opencv_utils as utils
from cli_args import setup_cli_args
from image_server import ImageServer

logger = logging.getLogger(__name__)

BLACK = np.uint8((0, 0, 0))


class ObjectTracker(object):
    def __init__(self,
                 width,
                 middle_percent,
                 display,
                 flip_x,
                 flip_y,
                 mask_x,
                 mask_y,
                 usb_camera,
                 usb_port,
                 camera_name,
                 http_host,
                 http_file,
                 http_delay_secs,
                 http_verbose):
        self.__width = width
        self.__middle_percent = middle_percent
        self.__orig_width = width
        self.__orig_middle_percent = middle_percent
        self.__display = display
        self.__flip_x = flip_x
        self.__flip_y = flip_y
        self.__mask_x = mask_x
        self.__mask_y = mask_y
        self.__filters = None

        self.__image = None
        self.stopped = False
        self.cnt = 0

        # Instantiate CvBridge
        self.bridge = CvBridge()

        self.image_server = ImageServer(http_file,
                                        camera_name=camera_name,
                                        http_host=http_host,
                                        http_delay_secs=http_delay_secs,
                                        http_verbose=http_verbose)

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        if 200 <= width <= 4000:
            self.__width = width
            if self.__filters:
                for f in self.__filters:
                    f.reset()

    @property
    def middle_percent(self):
        return self.__middle_percent

    @middle_percent.setter
    def middle_percent(self, val):
        if 2 <= val <= 98:
            self.__middle_percent = val
            if self.__filters:
                for filter in self.__filters:
                    filter.reset()

    @property
    def markup_image(self):
        return self.__display or self.image_server.enabled

    def __read_image(self, msg):
        try:
            cv2_img = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")

            cv2_img = imutils.resize(cv2_img, width=self.width)
            cv2_img = self.flip(cv2_img)

            # Apply masks
            if self.__mask_y != 0:
                height, width = cv2_img.shape[:2]
                mask_height = abs(int((self.__mask_y / 100.0) * height))
                if self.__mask_y < 0:
                    cv2_img[0: mask_height, 0: width] = BLACK
                else:
                    cv2_img[height - mask_height: height, 0: width] = BLACK

            if self.__mask_x != 0:
                height, width = cv2_img.shape[:2]
                mask_width = abs(int((self.__mask_x / 100.0) * width))
                if self.__mask_x < 0:
                    cv2_img[0: height, 0: mask_width] = BLACK
                else:
                    cv2_img[0: height, width - mask_width: width] = BLACK

            if self.__filters:
                for f in self.__filters:
                    f.process_image(cv2_img)
                for f in self.__filters:
                    if f.predicate:
                        f.predicate(f)
                    f.publish_data()
                    f.markup_image(cv2_img)

            self.image_server.image = cv2_img
            self.__image = cv2_img

            self.cnt += 1

        except KeyboardInterrupt as e:
            raise e
        except BaseException as e:
            rospy.logerr("Unexpected error in main loop [{0}]".format(e), exc_info=True)
            time.sleep(1)

    # Do not run this in a background thread. cv2.waitKey has to run in main thread
    def start(self, *filters):

        self.__filters = filters

        if self.__filters:
            for f in self.__filters:
                f.start()

        self.image_server.start()

        rospy.init_node('object_tracker')
        rospy.Subscriber('/raspicam_node/image/compressed', CompressedImage, self.__read_image)

        while not self.stopped:
            if self.__image is not None:
                self.display_image(self.__image)
            else:
                rospy.sleep(0.1)

    def stop(self):
        self.stopped = True

        if self.__filters:
            for f in self.__filters:
                f.stop()

        self.image_server.stop()

    def display_image(self, image):
        cv2.imshow("Image", image)

        key = cv2.waitKey(1) & 0xFF

        if key == 255:
            pass
        elif key == ord("w"):
            self.width -= 10
        elif key == ord("W"):
            self.width += 10
        elif key == ord("-") or key == ord("_") or key == 0:
            self.middle_percent -= 1
        elif key == ord("+") or key == ord("=") or key == 1:
            self.middle_percent += 1
        elif key == ord("r"):
            self.width = self.__orig_width
            self.middle_percent = self.__orig_middle_percent
        elif key == ord("s"):
            utils.write_image(image, log_info=True)
        elif key == ord("q"):
            self.stop()

    def flip(self, image):
        img = image
        if self.__flip_x:
            img = cv2.flip(img, 0)
        if self.__flip_y:
            img = cv2.flip(img, 1)
        return img

    @staticmethod
    def cli_args():
        return setup_cli_args(cli.bgr,
                              cli.usb_camera,
                              cli.usb_port,
                              cli.width,
                              cli.middle_percent,
                              cli.minimum_pixels,
                              cli.hsv_range,
                              cli.flip_x,
                              cli.flip_y,
                              cli.mask_x,
                              cli.mask_y,
                              cli.vertical_lines,
                              cli.horizontal_lines,
                              cli.camera_name_optional,
                              cli.display,
                              cli.draw_contour,
                              cli.draw_box,
                              cli.http_host,
                              cli.http_file,
                              cli.http_delay_secs,
                              cli.http_verbose,
                              cli.verbose)
