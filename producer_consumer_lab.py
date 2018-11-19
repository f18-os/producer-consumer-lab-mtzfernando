import base64
import queue
import time
from threading import Thread
import cv2
import numpy as np

extract_to_convert_queue = queue.Queue(10)                                          # The queue for extract producer to convert consumer
convert_to_display_queue = queue.Queue(10)                                          # The queue for convert producer to display consumer
done_extracting = False                                                             # Flag to signal the extraction is done
done_converting = False                                                             # Flag to signal the conversion is done
frame_delay = 47                                                                    # The delay for the frames
start_time = time.time()                                                            # Get the current time


class ExtractFrames(Thread):
    def run(self):
        count = 0                                                                   # Initialize the frame count
        global extract_to_convert_queue, done_extracting

        video_capture = cv2.VideoCapture('clip.mp4')                                # Open the video clip
        success, image = video_capture.read()                                       # Read one frame

        print("Reading frame {} {} ".format(count, success))

        while success:                                                              # Go through each frame in the buffer
            extract_to_convert_queue.put(image)                                     # Add the frame to the buffer

            success, image = video_capture.read()                                   # Read one frame
            count += 1
            print('Reading frame {} {}'.format(count, success))

        print("Frame extraction complete")
        done_extracting = True                                                      # Signal done extracting


class ConvertToGrayScale(Thread):
    def run(self):
        count = 0                                                                   # Initialize frame count to convert
        global extract_to_convert_queue, done_converting

        while not done_extracting or not extract_to_convert_queue.empty():          # Go through each frame in the buffer
            image = extract_to_convert_queue.get()                                  # Get the frame from the queue

            print("Converting frame {}".format(count))

            gray_scale_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)              # Convert the image to gray scale
            success, jpg_image = cv2.imencode('.jpg', gray_scale_frame)             # Get a jpg encoded frame
            jpg_as_text = base64.b64encode(jpg_image)                               # Encode the frame as base 64 to make debugging easier
            convert_to_display_queue.put(jpg_as_text)                               # Add the frame to the buffer
            count += 1

        print("Frame conversion complete")
        done_converting = True


class DisplayFrames(Thread):
    def run(self):
        global convert_to_display_queue, done_extracting, start_time
        count = 0                                                                   # Initialize frame count

        while not done_converting or not convert_to_display_queue.empty():          # Go through each frame in the buffer
            frameAsText = convert_to_display_queue.get()                            # Get the next frame
            jpgRawImage = base64.b64decode(frameAsText)                             # Decode the frame
            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)           # Convert the raw frame to a numpy array
            img = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)                      # Get a jpg encoded frame

            print("Displaying frame {}".format(count))

            # display the image in a window called "video" and wait 47ms before displaying the next frame
            cv2.imshow("Video", img)

            # Compute the amount of time that has elapsed while the frame was processed
            elapsed_time = int((time.time() - start_time) * 1000)

            # Determine the amount of time to wait, also make sure we don't go into negative time
            time_to_wait = max(1, frame_delay - elapsed_time)

            if cv2.waitKey(time_to_wait) and 0xFF == ord("q"):                      # Wait for 47ms and check if the user wants to quit
                break
            count += 1

        print("Finished displaying all frames")
        cv2.destroyAllWindows()                                                     # Cleanup the windows


ExtractFrames().start()                                                             # Start the extract thread
ConvertToGrayScale().start()                                                        # Start the convert thread
DisplayFrames().start()                                                             # Start the display thread
