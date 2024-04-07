from ai_model_dispatcher.dispatcher.BaseDispatcher import BaseDispatcher


class DynamicProxy:

    def __init__(self, model_name):
        self.model_name = model_name
    def __getattr__(self, method_name):
        if method_name is not None:
            return lambda *args, **kwargs: self.method_impl(method_name, *args, **kwargs)
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{method_name}'")

    def method_impl(self, method_name, *args, **kwargs):
        dispatcher = BaseDispatcher()
        result = dispatcher.call(model_name=self.model_name, method=method_name,
                                 params=kwargs)
        return result.get('data')
