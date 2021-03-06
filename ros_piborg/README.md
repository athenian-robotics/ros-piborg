# ros-piborg 


Run piborg_controller with:
```bash
$ rosrun ros_piborg piborg_controller.py
```

Run process_image with:
```bash
$ rosrun ros_piborg process_image.py
```

$ rosrun ros_piborg ros_color_picker.py -x --img_topic /raspicam_node/image/compressed --compressed 


$ rosrun ros_piborg local_color_picker.py --width 700

$ rosrun ros_piborg local_single_object.py -x --bgr "174, 56, 5" --http rosborg.local
$ rosrun ros_piborg local_single_object.py -x --bgr "174, 56, 5" --vertical_lines --horizontal_lines --draw_box --http rosborg.local

python file_color_picker.py -f ../images/IMG_3248.jpg

$ rosrun ros_piborg video_single_object.py -f ~/catkin_ws/src/ros-piborg/ros_piborg/images/track.m4v --bgr "93, 211, 245" --draw_box --draw_contour --http paris.local

# Race Track on video
$ rosrun ros_piborg video_multi_object.py -f ~/catkin_ws/src/ros-piborg/ros_piborg/images/track.m4v --bgr "93, 211, 245" --draw_line --draw_box --draw_contour --http paris.local --hsv 5 --max_objects 8 --min_pixels 500 --fps 30 --width 900

# Race track on Raspi
$ rosrun ros_piborg local_multi_object.py --bgr "93, 211, 245" --draw_line  --draw_box --draw_contour --http rosborg.local --hsv 5 --max_objects 8 --min_pixels 500 --width 900
$ rosrun ros_piborg local_multi_object.py --bgr "71, 199, 197" --draw_line  --draw_box --draw_contour --http rosborg.athenian.org --hsv 5 --max_objects 8 --min_pixels 500 --width 900


roslaunch raspicam_node camerav2_1280x960.launch

Install *raspicam_node* as described [here](https://github.com/UbiquityRobotics/raspicam_node).