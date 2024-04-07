from ai_model_base.model.BaseModel import BaseModel


class ModelFactory:

    @staticmethod
    def create_by_class(model_class):
        model: BaseModel = model_class()
        model.startup()
        return model
