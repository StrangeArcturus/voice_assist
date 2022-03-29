import base_voice_assistant as base_voice_assistant
import voice_assistant_internet as voice_assistant_internet


class VoiceAssistantWithAllSkills(
    voice_assistant_internet.VoiceAssistantWithInternetSkills,
    base_voice_assistant.VoiceAssistantWithGUIControl
    ):
    """
    Класс, объединяющий все базовые модели ассистента
    """
    ...
