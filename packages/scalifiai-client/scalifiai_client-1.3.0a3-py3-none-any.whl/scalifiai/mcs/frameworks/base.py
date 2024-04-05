from scalifiai.mcs.frameworks.exceptions import ModelWrapperInvalidModelException


class ModelWrapper:
    # TODO[VIMPORTANT] CHECK AND MAKE FUNCTIONS PRIVATE IF THEY SHOULD NOT BE ACCESSIBLE DIRECTLY

    def __init__(self, *, model=None) -> None:

        if model == None:
            raise ModelWrapperInvalidModelException()

        self.model = model

    def infer_data_type(self, *, dtype):
        pass

    def infer_signature(self):
        pass
