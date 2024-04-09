from pydantic import BaseModel


class ClipSavePayload(BaseModel):
    """The payload for all clip save endpoints.
    start and end are the timestamps of the final clip relative to the extended clip timstamps.
    E.g. An extended clip starts on second 10 and ends on second 100 of the source clip. The values for
    start and end in ClipSavePayload are 25 and 50. This will create a final clip that starts on second 35 (10 + 25)
    and ends on second 60 (10 + 50)."""

    start: float
    end: float

    def to_json(self):
        return {"start": self.start, "end": self.end}
