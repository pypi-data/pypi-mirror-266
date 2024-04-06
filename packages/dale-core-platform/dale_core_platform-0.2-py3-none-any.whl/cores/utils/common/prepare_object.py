from ...model import RequestObjModel


class PrepareObj:

    @staticmethod
    def preparation(Model) -> RequestObjModel:
        return RequestObjModel(**Model)
