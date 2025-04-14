import logging
from common.registry import Registry


@Registry.register_task('base')
class BaseTask:
    '''
    Register BaseTask, currently support TSC task.
    '''
    def __init__(self, trainer):
        self.trainer = trainer

    def run(self):
        raise NotImplementedError

    def _process_error(self, e):
        e_str = str(e)
        if (
            "find_unused_parameters" in e_str
        ):
            for name, parameter in self.trainer.agents.model.named_parameters():
                if parameter.requires_grad and parameter.grad is None:
                    logging.warning(
                        f"Parameter {name} has no gradient. Consider removing it from the model."
                    )


@Registry.register_task("tsc")
class TSCTask(BaseTask):
    '''
    Register Traffic Signal Control task.
    增加了设置信号状态回调的接口，用于记录或展示信号灯方案。
    '''

    # def __init__(self, trainer):
    #     super().__init__(trainer)
    #     self.signal_callback = None
    #
    # def set_signal_callback(self, callback):
    #     """
    #     注册信号状态回调函数，在环境步进时调用。
    #     如果 trainer 内部也支持设置信号回调，可以同时传递给 trainer。
    #     """
    #     self.signal_callback = callback
    #     if hasattr(self.trainer, 'set_signal_callback'):
    #         self.trainer.set_signal_callback(callback)


    '''
    Register Traffic Signal Control task.
    '''
    def run(self):
        '''
        run
        Run the whole task, including training and testing.

        :param: None
        :return: None
        '''
        try:
            if Registry.mapping['model_mapping']['setting'].param['train_model']:
                self.trainer.train()
            if Registry.mapping['model_mapping']['setting'].param['test_model']:
                self.trainer.test()
        except RuntimeError as e:
            self._process_error(e)
            raise e
