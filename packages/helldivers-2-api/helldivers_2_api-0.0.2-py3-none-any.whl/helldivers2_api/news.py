from dataclasses import dataclass


@dataclass
class News:
    news_id: int
    published: int
    type: int  # ToDo: Unclear what this is for, it seems to be always 0
    tagIds: list[int]
    message: str
