import cv2

import cv2

import opencv_defaults as defs
from generic_filter import GenericFilter
from opencv_utils import BLUE, GREEN, RED, YELLOW
from opencv_utils import get_moment


class DualObjectFilter(GenericFilter):
    def __init__(self, tracker, *args, **kwargs):
        super(DualObjectFilter, self).__init__(tracker, *args, **kwargs)
        self.contour1, self.contour2 = None, None
        self.img_x1, self.img_y1 = -1, -1
        self.img_x2, self.img_y2 = -1, -1
        self.avg_x, self.avg_y = -1, -1
        self.height, self.width = None, None

    def reset_data(self):
        self.avg_x, self.avg_y = -1, -1

    def process_image(self, image):
        self.contour1, self.contour2 = None, None
        self.reset_data()
        self.height, self.width = image.shape[:2]

        # Find the 2 largest vertical contours
        self.contours = self.contour_finder.get_max_contours(image, count=2)
        # self.contours = self.contour_finder.get_max_vertical_contours(image, count=2)

        # Check for > 2 in case one of the targets is divided.
        # The calculation will be off, but something will be better than nothing
        if self.contours is not None and len(self.contours) >= 2:
            self.contour1, area1, self.img_x1, self.img_y1 = get_moment(self.contours[0])
            self.contour2, area2, self.img_x2, self.img_y2 = get_moment(self.contours[1])

            # Calculate the average location between the two midpoints
            self.avg_x = (abs(self.img_x1 - self.img_x2) / 2) + min(self.img_x1, self.img_x2)
            self.avg_y = (abs(self.img_y1 - self.img_y2) / 2) + min(self.img_y1, self.img_y2)

    def publish_data(self):
        # Write location if it is different from previous value written
        if self.avg_x != self.prev_x or self.avg_y != self.prev_y:
            self.location_server.write_location(self.avg_x, self.avg_y, self.width, self.height, self.middle_inc)
            self.prev_x, self.prev_y = self.avg_x, self.avg_y

    def markup_image(self, image):
        mid_x, mid_y = self.width / 2, self.height / 2
        mid_inc = int(self.middle_inc)

        x_in_middle = mid_x - mid_inc <= self.avg_x <= mid_x + mid_inc
        y_in_middle = mid_y - mid_inc <= self.avg_y <= mid_y + mid_inc
        x_color = GREEN if x_in_middle else RED if self.avg_x == -1 else BLUE
        y_color = GREEN if y_in_middle else RED if self.avg_y == -1 else BLUE

        if not self.tracker.markup_image:
            return

        text = "#{0} ({1}, {2})".format(self.tracker.cnt, self.width, self.height)
        text += " {0}%".format(self.tracker.middle_percent)

        if self.contours is not None and len(self.contours) >= 2:
            x1, y1, w1, h1 = cv2.boundingRect(self.contour1)
            x2, y2, w2, h2 = cv2.boundingRect(self.contour2)

            if self.draw_box:
                cv2.rectangle(image, (x1, y1), (x1 + w1, y1 + h1), BLUE, 2)
                cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), BLUE, 2)

            if self.draw_contour:
                cv2.drawContours(image, [self.contour1], -1, GREEN, 2)
                cv2.drawContours(image, [self.contour2], -1, GREEN, 2)

            cv2.circle(image, (self.img_x1, self.img_y1), 4, RED, -1)
            cv2.circle(image, (self.img_x2, self.img_y2), 4, RED, -1)

            # Draw midpoint
            cv2.circle(image, (self.avg_x, self.avg_y), 4, YELLOW, -1)
            text += " Avg: ({0}, {1})".format(self.avg_x, self.avg_y)

        # Draw the alignment lines
        if self.vertical_lines:
            cv2.line(image, (mid_x - mid_inc, 0), (mid_x - mid_inc, self.height), x_color, 1)
            cv2.line(image, (mid_x + mid_inc, 0), (mid_x + mid_inc, self.height), x_color, 1)

        if self.horizontal_lines:
            cv2.line(image, (0, mid_y - mid_inc), (self.width, mid_y - mid_inc), y_color, 1)
            cv2.line(image, (0, mid_y + mid_inc), (self.width, mid_y + mid_inc), y_color, 1)

        if self.display_text:
            cv2.putText(image, text, defs.TEXT_LOC, defs.TEXT_FONT, defs.TEXT_SIZE, RED, 1)