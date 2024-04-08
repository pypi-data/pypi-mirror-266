from pydantic import BaseModel


class SubtitleSettings(BaseModel):
    font: str = "DejaVu Serif"
    font_size: int = 20

    def to_json(self):
        return {
            "font": self.font,
            "font_size": self.font_size,
        }
