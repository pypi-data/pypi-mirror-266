class CustomError(Exception):
    def __init__(self, error_text):
        self.error_text = error_text


class RaiseErrors:
    def __init__(self):
        self.automations_errors = {401: CustomError("Wrong API key for disable automations"),
                                   404: CustomError("Wrong HA host or port for disable automations")}

    def raise_error(self, error_code: int, error_dict: dict[int: any]):
        raise_error = error_dict.get(error_code)
        if raise_error:
            raise raise_error
