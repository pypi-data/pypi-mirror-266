from diffusion.internal.serialisers.pydantic import MarshalledModel


class SessionLockRequestCancellation(MarshalledModel):
    """
    The request to cancel a session lock.
    """
    lock_name: str
    request_id: int

    class Config(MarshalledModel.Config):
        frozen = True
        alias_generator = None

        @classmethod
        def attr_mappings_all(cls, modelcls):
            return {
                "session-lock-request-cancellation": {
                    "session-lock-name": "lock_name",
                    "session-lock-request-id": "request_id",
                }
            }

    def __str__(self):
        return f"{type(self).__name__}[{self.lock_name}, {self.request_id}]"
