from enum import Enum
from typing import List
from pydantic import BaseModel

from fastclip.enums.ClipFormat import ClipFormat
from fastclip.schemas.SubtitleSettings import SubtitleSettings
from fastclip.schemas.Word import Word

# The default duration in seconds to extend the clip by if the extend type is set to START or END
EXTEND_DURATION = 30


class ExtendType(Enum):
    """What type of clip extension to use.
    NONE: Clip preview timestamps are not changed
    START: Clip preview start timestamp is extended
    END: Clip preview end timestamp is extended"""

    NONE = "none"
    START = "start"
    END = "end"


class ClipPreviewPayload(BaseModel):
    """The payload for all clip preview endpoints.
    There are two concepts here:
    1. The clip: The actual clip that will be previewed
    2. The extended clip: The clip that will be previewed with the extension applied
    The extended clip allows the user to move the start or end of the clip to make it better.
    """

    # The start and end of the actual clip
    start: float
    end: float

    subtitles_settings: SubtitleSettings
    subtitles: List[Word] = []
    format: ClipFormat = ClipFormat.HORIZONTAL
    has_subtitles: bool = False

    # Extended clip properties
    extend: ExtendType = ExtendType.NONE
    extended_start: float = 0
    extended_end: float = 0

    def to_json(self):
        return {
            "start": self.start,
            "end": self.end,
            "subtitles_settings": self.subtitles_settings.to_json(),
            "subtitles": [word.to_json() for word in self.subtitles],
            "format": self.format.value,
            "has_subtitles": self.has_subtitles,
            "extended_start": self.extended_start,
            "extended_end": self.extended_end,
        }
