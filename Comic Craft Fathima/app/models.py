from pydantic import BaseModel, Field, ConfigDict

class PromptRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    story_prompt: str = Field(min_length=3, max_length=2000)
    character_name: str = Field(default="Alex", min_length=1, max_length=80)
    setting: str = Field(default="A mysterious forest", min_length=1, max_length=200)
    tone: str = Field(default="funny", min_length=1, max_length=80)
    art_style: str = Field(default="comic book", min_length=1, max_length=100)

class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str

class ComicOutline(BaseModel):
    panels: list[PanelOutline]

class PanelStory(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str

class ComicStory(BaseModel):
    panels: list[PanelStory]

class ComicLayoutItem(BaseModel):
    panel_number: int
    title: str
    image_path: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str
