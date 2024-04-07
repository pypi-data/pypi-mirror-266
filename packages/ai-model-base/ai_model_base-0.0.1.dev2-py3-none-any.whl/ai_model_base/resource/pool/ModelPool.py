from ai_model_base.model.BaseModel import BaseModel
from ai_model_base.resource.factory.ModelFactory import ModelFactory
from ai_model_base.resource.proxy.DynamicProxy import DynamicProxy


class ModelPool:
    pool: dict[str, BaseModel] = {}

    def get_model_by_name(self, model_name):
        return DynamicProxy(model_name)

    def get_model_by_class(self, model_class):
        model_name = model_class.__name__
        if model_name in self.pool:
            pass
        else:
            model = ModelFactory.create_by_class(model_class)
            self.pool[model_name] = model
        return self.pool.get(model_name)

    def list_active_model_name(self):
        return set(self.pool.keys())

    def release_model_by_name(self, model_name):
        if model_name in self.pool:
            model = self.pool.get(model_name)
            model.shutdown()
            del self.pool[model_name]
            return True
        else:
            return False


model_pool = ModelPool()
