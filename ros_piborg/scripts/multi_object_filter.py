import cv2

import cli_args  as cli
import opencv_defaults as defs
from generic_filter import GenericFilter
from opencv_utils import BLUE, GREEN, RED, YELLOW
from opencv_utils import get_moment


class MultiObjectFilter(GenericFilter):
    args = [cli.so_topic, cli.bgr, cli.hsv_range, cli.min_pixels, cli.draw_contour,
            cli.draw_box, cli.vert_lines, cli.horiz_lines]

    def __init__(self, tracker, *args, **kwargs):
        super(MultiObjectFilter, self).__init__(tracker, *args, **kwargs)
        self.moments = None
        self.contours = None
        self.height, self.width = None, None

    def reset_data(self):
        self.moments = []
        self.contours = None

    def process_image(self, image):
        self.reset_data()
        self.height, self.width = image.shape[:2]

        self.contours = self.contour_finder.get_max_contours(image, count=20000)

        # Check for > 2 in case one of the targets is divided.
        # The calculation will be off, but something will be better than nothing
        if self.contours is not None:
            for i in range(len(self.contours)):
                self.moments.append(get_moment(self.contours[i]))

    def publish_data(self):
        # Write location if it is different from previous value written
        # if self.avg_x != self.prev_x or self.avg_y != self.prev_y:
        # self.location_server.write_location(self.avg_x, self.avg_y, self.width, self.height, self.middle_inc)
        #    self.prev_x, self.prev_y = self.avg_x, self.avg_y
        pass

    def markup_image(self, image):
        mid_x, mid_y = self.width / 2, self.height / 2
        mid_inc = int(self.middle_inc)

        # x_in_middle = mid_x - mid_inc <= self.avg_x <= mid_x + mid_inc
        # y_in_middle = mid_y - mid_inc <= self.avg_y <= mid_y + mid_inc
        # x_color = GREEN if x_in_middle else RED if self.avg_x == -1 else BLUE
        #y_color = GREEN if y_in_middle else RED if self.avg_y == -1 else BLUE

        if not self.tracker.markup_image:
            return

        text = "#{0} ({1}, {2})".format(self.tracker.cnt, self.width, self.height)
        text += " {0}%".format(self.tracker.middle_percent)

        if self.contours is not None:
            for i in range(len(self.contours)):
                x, y, w, h = cv2.boundingRect(self.contours[i])

                if self.draw_box:
                    cv2.rectangle(image, (x, y), (x + w, y + h), BLUE, 2)

                if self.draw_contour:
                    cv2.drawContours(image, [self.contours[i]], -1, GREEN, 2)

                # Draw center
                cv2.circle(image, (self.x, self.y), 4, YELLOW, -1)

                #text += " Avg: ({0}, {1})".format(self.avg_x, self.avg_y)

        # Draw the alignment lines
        # if self.vertical_lines:
        #    cv2.line(image, (mid_x - mid_inc, 0), (mid_x - mid_inc, self.height), x_color, 1)
        #    cv2.line(image, (mid_x + mid_inc, 0), (mid_x + mid_inc, self.height), x_color, 1)

        # if self.horizontal_lines:
        #    cv2.line(image, (0, mid_y - mid_inc), (self.width, mid_y - mid_inc), y_color, 1)
        #    cv2.line(image, (0, mid_y + mid_inc), (self.width, mid_y + mid_inc), y_color, 1)

        if self.display_text:
            cv2.putText(image, text, defs.TEXT_LOC, defs.TEXT_FONT, defs.TEXT_SIZE, RED, 1)
