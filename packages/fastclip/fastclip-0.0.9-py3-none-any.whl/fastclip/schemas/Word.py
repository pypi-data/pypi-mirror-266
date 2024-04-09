from fastclip.schemas.AbstractTranscriptComponent import (
    AbstractTranscriptComponent,
)


class Word(AbstractTranscriptComponent):
    """Represents a word in a transcript."""

    word: str
    punctuated_word: str
    start: float
    end: float

    def __repr__(self):
        return f"Word(word='{self.word}', punctuated_word='{self.punctuated_word}', start={self.start}, end={self.end})"

    def to_json(self):
        return {
            "word": self.word,
            "punctuated_word": self.punctuated_word,
            "start": self.start,
            "end": self.end,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            word=d["word"],
            punctuated_word=d["punctuated_word"],
            start=d["start"],
            end=d["end"],
        )
