from translation import Translation, translator
from owner_person import OwnerPerson, person

from __voice_assistant import VoiceAssistant
from __voice_assistant_internet import VoiceAssistantWithInternetSkills

import random
import traceback


class VoiceAssistantWithAllSkills(VoiceAssistantWithInternetSkills):
    ...


assistant = VoiceAssistantWithAllSkills(translator, person)
