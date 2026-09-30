from app.models import ComicLayoutItem, ComicOutline, ComicStory

def build_comic_layout(outline: ComicOutline, story: ComicStory, image_paths: list[str]) -> list[ComicLayoutItem]:
    outline_by_number = {p.panel_number: p for p in outline.panels}
    story_by_number = {p.panel_number: p for p in story.panels}

    layout = []
    for index, image_path in enumerate(image_paths, start=1):
        outline_panel = outline_by_number[index]
        story_panel = story_by_number[index]
        layout.append(
            ComicLayoutItem(
                panel_number=index,
                title=story_panel.title or outline_panel.title,
                image_path=image_path,
                scene_description=story_panel.scene_description or outline_panel.scene_description,
                caption=story_panel.caption,
                narration=story_panel.narration,
                dialogue=story_panel.dialogue,
                image_prompt=outline_panel.image_prompt,
            )
        )
    return layout
