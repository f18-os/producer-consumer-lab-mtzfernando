import base64
import queue
from threading import Thread
import cv2
import numpy as np

extract_to_convert_queue = queue.Queue(10)
convert_to_display_queue = queue.Queue(10)
done_extracting = False
done_converting = False


class ExtractFrames(Thread):
    def run(self):
        video_capture = cv2.VideoCapture('clip.mp4')
        count = 0
        global extract_to_convert_queue, done_extracting
        # read one frame
        success, image = video_capture.read()

        print("Reading frame {} {} ".format(count, success))
        while success:
            # add the frame to the buffer
            extract_to_convert_queue.put(image)

            success, image = video_capture.read()
            count += 1
            print('Reading frame {} {}'.format(count, success))

        print("Frame extraction complete")
        done_extracting = True


class ConvertToGrayScale(Thread):
    def run(self):
        global extract_to_convert_queue, done_converting

        # initialize frame count
        count = 0

        while not done_extracting or not extract_to_convert_queue.empty():
            image = extract_to_convert_queue.get()

            print("Converting frame {}".format(count))

            # convert the image to gray scale
            gray_scale_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # get a jpg encoded frame
            success, jpg_image = cv2.imencode('.jpg', gray_scale_frame)

            # encode the frame as base 64 to make debugging easier
            jpg_as_text = base64.b64encode(jpg_image)

            # add the frame to the buffer
            convert_to_display_queue.put(jpg_as_text)
            count += 1
        print("Frame conversion complete")
        done_converting = True


class DisplayFrames(Thread):
    def run(self):
        global convert_to_display_queue, done_extracting

        # initialize frame count
        count = 0

        # go through each frame in the buffer until the buffer is empty
        while not done_converting or not convert_to_display_queue.empty():
            # get the next frame
            frameAsText = convert_to_display_queue.get()

            # decode the frame
            jpgRawImage = base64.b64decode(frameAsText)

            # convert the raw frame to a numpy array
            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

            # get a jpg encoded frame
            img = cv2.imdecode(jpgImage, cv2.IMREAD_UNCHANGED)

            print("Displaying frame {}".format(count))

            # display the image in a window called "video" and wait 42ms
            # before displaying the next frame
            cv2.imshow("Video", img)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break

            count += 1

        print("Finished displaying all frames")
        # cleanup the windows
        cv2.destroyAllWindows


video_name = 'clip.mp4'
ExtractFrames().start()
ConvertToGrayScale().start()
DisplayFrames().start()
