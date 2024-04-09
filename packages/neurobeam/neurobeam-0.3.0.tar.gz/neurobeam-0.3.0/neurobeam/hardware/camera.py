import warnings
from typing import Any, Optional
from multiprocessing import Process, Queue, Pipe
from pathlib import Path
from operator import eq
from time import sleep

import cv2 as cv
import numpy as np

from ..configs import HoistedConfig
from ..data import TimestampedRingBuffer
from ..exceptions import DualUserInterfaceError
from ..registries import Provider
from ..tools import PatternMatching, HAS


def stream_video(camera_idx: int = 0,
                 height: int = 480,
                 width: int = 640,
                 quarter_period: float = 8.33,
                 display_name: Optional[str] = None,
                 image_queue: Optional[Queue] = None,
                 command_pipe: Optional[Pipe] = None,
                 output_file: Optional[Path] = None
                 ) -> None:

    if output_file:
        ring_buffer = TimestampedRingBuffer(element_depth=height,
                                            element_length=width,
                                            ring_size=1,
                                            path=output_file,
                                            dtype=np.uint8,
                                            do_reorganize=False)
    else:
        ring_buffer = None

    # XOR VALIDATION - MUST HAVE DISPLAY OR GUI
    if not (bool(display_name) ^ bool(image_queue)):  # pragma: no cover
        raise DualUserInterfaceError

    # MAKE WINDOW FOR DISPLAY NAME
    if display_name:
        cv.namedWindow(display_name, cv.WINDOW_NORMAL)

    # CREATE CAMERA FEED
    cam = cv.VideoCapture(camera_idx, cv.CAP_DSHOW)
    #cam = cv.VideoCapture(camera_idx, cv.CAP_MSMF)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)
    cam.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    # RUN CAMERA LOOP
    while True:
        # Ensure camera is connected & attempt to read frame
        if cam.isOpened():
            (status, frame) = cam.read()
            if frame.ndim > 2:  # necessary evil to convert to grayscale
                frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # Do whatever user wishes with the video frame
            with PatternMatching([bool(status), bool(image_queue), bool(ring_buffer)],
                                 [eq, eq, eq]) as case:
                if case([True, True, True]):
                    image_queue.put_nowait(frame)
                    ring_buffer.add_data(frame)
                elif case([True, True, False]):
                    image_queue.put_nowait(frame)
                elif case([True, False, True]):
                    cv.imshow(display_name, frame)
                    ring_buffer.add_data(frame)
                    cv.waitKey(quarter_period)
                elif case([True, False, False]):
                    cv.imshow(display_name, frame)
                    cv.waitKey(quarter_period)
                else:  # pragma: no cover
                    warnings.warn(CameraCollectionWarning(camera_idx))

                if command_pipe.poll():
                    command = command_pipe.recv()
                    if command == "stop":
                        cam.release()
        else:
            if ring_buffer:
                ring_buffer.close()
            break

    cv.destroyAllWindows()


@Provider()
class Camera:
    """
    Camera class for handling camera feeds
    """
    def __init__(self, config: Optional["HoistedConfig"],
                 camera_idx: int = 0,
                 height: int = 480,
                 width: int = 640,
                 fps: float = 30.0,
                 save_video: bool = False,
                 use_gui: bool = False,
                 output_file: Path = Path.cwd().joinpath("camera_output")
                 ):
        """
        Camera class for handling camera feeds

        :param config: The configuration with a hoisted camera config
        :param camera_idx: The index of the camera (used if config is not provided)
        :param height: The height of the camera feed (used if config is not provided)
        :param width: The width of the camera feed (used if config is not provided)
        :param fps: The frames per second of the camera feed (used if config is not provided)
        :param output_file: The output file for saving (used if config is not provided)
        :param save_video: Whether to save the video (used if config is not provided)
        :param use_gui: Whether to use the gui (used if config is not provided)
        """
        ################################################################################################################
        # CONFIGURE
        ################################################################################################################
        #: Config: reference to the configuration
        self.config = config
        #: int: camera index
        self.camera_idx = config.camera_idx if HAS(config) else camera_idx
        #: int: height of the camera feed
        self.height = self.config.height if HAS(config) else height
        #: int: width of the camera feed
        self.width = self.config.width if HAS(config) else width
        #: float: frames per second
        self.fps = self.config.fps if HAS(config) else fps
        #: Path: output file for saving
        self.output_file = self.config.save_location.joinpath(self.config.file_header + f"camera_{self.camera_idx}") \
            if HAS(config) else output_file
        #: bool: whether to use the gui
        self.use_gui = self.config.use_gui if HAS(config) else use_gui
        #: bool: whether to save
        self.save = self.config.save_video if HAS(config) else save_video
        #: Queue: queue of images for display
        self.image_queue = None
        #: Pipe: command pipe
        self.command_pipe = None
        #: Process: camera process
        self.camera = None
        # only set display name if not in gui mode
        self._display_name = None if self.use_gui else f"Camera: {self.camera_idx}"
        self.build()

    def __str__(self) -> str:
        return f"Camera{self.camera_idx}: {self.height}x{self.width} @ {self.fps} fps"

    def __name__(self) -> str:
        return f"Camera{self.camera_idx}"

    @property
    def quarter_period(self) -> float:
        """
        Calculate the quarter period of the camera feed in milliseconds
        """
        return round(1 / self.fps * 1000 / 4)

    def build(self) -> None:
        """
        Build the camera process
        """
        if self.use_gui:
            self.image_queue = Queue(maxsize=1)
        self.command_pipe, command_pipe = Pipe()
        self.camera = Process(name=f"Camera{ self.camera_idx}",
                              target=stream_video,
                              args=(self.camera_idx,
                                    self.height,
                                    self.width,
                                    self.quarter_period,
                                    self._display_name,
                                    self.image_queue,
                                    command_pipe,
                                    self.output_file))

    def start(self) -> None:
        """
        Start the camera process
        """
        self.camera.start()

    def stop(self) -> None:
        """
        Stop the camera process by sending a stop command through the command pipe. This will alert the camera to stop
        and save close the file handle if it was initialized to the save video.
        """
        if self.camera:
            self.command_pipe.send("stop")
            sleep(1)
            self.camera.terminate()
            sleep(1)
            self.camera.join(timeout=5.0)

    def destroy(self) -> None:
        """
        Terminate the camera process
        """
        if self.camera:
            self.camera.terminate()

    def __del__(self):
        if self.camera:
            self.camera.terminate()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):

        if self.camera:
            self.camera.terminate()


if __name__ == "__main__":
    # Protection from running the module as a script
    pass
