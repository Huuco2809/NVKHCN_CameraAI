"""
manh.truongle  - Nov 23, 2021
truonnglm.spk@gmail.com
base wrapper
"""
import abc


class BaseWrapper(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def init(self, *args, **kwargs):
        """load model and init (if any)"""

    @abc.abstractmethod
    def proceed(self, *args, **kwargs):
        """
        main function,
        processing input and return output
        """
        pass


class AIBaseWrapper(BaseWrapper):
    def __init__(self):
        super().__init__()
        self._model = None  # this is variable store model
        self._device = None  # set device

    @abc.abstractmethod
    def _load_model(self, *args, **kwargs):
        """load model from weight"""
        pass

    def _check_model_init(self, logger=None):
        if self._model is None:
            if logger:
                logger.warning("model has not been initialized. Re-initialize model now ...")
            self.init()

    @abc.abstractmethod
    def _pre_process(self, *args, **kwargs):
        """
        pre-process input data before processing
        """
        pass

    @abc.abstractmethod
    def _post_process(self, *args, **kwargs):
        """
        post-process output
        """
        pass



