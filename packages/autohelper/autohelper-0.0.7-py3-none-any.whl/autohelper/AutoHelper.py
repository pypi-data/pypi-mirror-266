import threading
import time
from typing import Dict, Any

import autohelper
from autohelper.feature.FeatureSet import FeatureSet
from autohelper.gui.App import App
from autohelper.gui.Communicate import communicate
from autohelper.gui.util.InitWorker import InitWorker
from autohelper.logging.Logger import get_logger, config_logger
from autohelper.task.TaskExecutor import TaskExecutor

logger = get_logger(__name__)


class AutoHelper:
    executor: TaskExecutor
    adb = None
    adb_device = None
    feature_set = None
    hwnd = None
    device_manager = None
    ocr = None

    def __init__(self, config: Dict[str, Any]):
        print(f"AutoHelper init, config: {config}")
        self.debug = config.get("debug", False)
        self.exit_event = threading.Event()
        self.config = config
        self.init_adb()
        if config.get("use_gui"):
            self.app = App(self.config.get('gui_icon'), self.debug, self.config.get('gui_title'),
                           self.config['tasks'], self.exit_event)
            autohelper.gui.app = self.app
            self.app.show_loading()
            self.worker = InitWorker(self.do_init)
            self.worker.start()
            self.app.exec()
        else:
            self.do_init()
            try:
                # Starting the task in a separate thread (optional)
                # This allows the main thread to remain responsive to keyboard interrupts
                task_thread = threading.Thread(target=self.wait_task())
                task_thread.start()

                # Wait for the task thread to end (which it won't, in this case, without an interrupt)
                task_thread.join()
            except KeyboardInterrupt:
                self.exit_event.set()
                logger.info("Keyboard interrupt received, exiting script.")
            finally:
                # Clean-up code goes here (if any)
                # This block ensures that the script terminates gracefully,
                # releasing resources or performing necessary clean-up operations.
                logger.info("Script has terminated.")

    def init_message(self, message: str, done=False):
        communicate.init.emit(done, message)
        if self.exit_event.is_set():
            self.worker.quit()

    def do_init(self):
        logger.info(f"initializing {self.__class__.__name__}, config: {self.config}")
        if self.config.get('ocr'):
            self.init_message("RapidOCR init Start")
            from rapidocr_onnxruntime import RapidOCR
            self.ocr = RapidOCR()
            self.init_message("RapidOCR init Complete")

        config_logger(self.config)

        if self.config.get('coco_feature_folder') is not None:
            self.init_message("FeatureSet init Start")
            coco_feature_folder = self.config.get('coco_feature_folder')
            self.feature_set = FeatureSet(coco_feature_folder,
                                          default_horizontal_variance=self.config.get('default_horizontal_variance', 0),
                                          default_vertical_variance=self.config.get('default_vertical_variance', 0),
                                          default_threshold=self.config.get('default_threshold', 0))
            self.init_message("FeatureSet init Complete")

        self.init_message("TaskExecutor init Start")
        self.task_executor = TaskExecutor(self.device_manager, exit_event=self.exit_event,
                                          tasks=self.config['tasks'], scenes=self.config['scenes'],
                                          feature_set=self.feature_set,
                                          ocr=self.ocr, config_folder=self.config.get("config_folder") or "config")
        self.init_message("TaskExecutor init Done")

        if self.app:
            autohelper.gui.executor = self.task_executor

    def wait_task(self):
        while not self.exit_event.is_set():
            time.sleep(1)

    def init_adb(self):
        if self.device_manager is None:
            from autohelper.capture.adb.DeviceManager import DeviceManager
            self.device_manager = DeviceManager(self.config.get("config_folder") or "config",
                                                self.config.get('capture_window_title'), self.config.get("debug"),
                                                self.exit_event)
            autohelper.gui.device_manager = self.device_manager
