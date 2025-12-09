"""
manh.truongle - Nov 23, 2021
truonnglm.spk@gmail.com
base api
"""
import abc


class BaseAPI(object, metaclass=abc.ABCMeta):
    def __init__(self):
        self._initialized = None

    @abc.abstractmethod
    def init(self, *args, **kwargs):
        """
        init all modules
        """
        pass

    def _check_init(self, logger=None):
        if self._initialized is None:
            if logger:
                logger.warning("API has not been initialized. Re-initialize model now ...")
            self.init()

    @abc.abstractmethod
    def proceed(self, *args, **kwargs):
        """
        main function,
        process input and return output
        """
        pass
