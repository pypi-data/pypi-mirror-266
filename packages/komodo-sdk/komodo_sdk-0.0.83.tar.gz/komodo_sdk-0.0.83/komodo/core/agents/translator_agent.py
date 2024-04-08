from komodo.framework.komodo_agent import KomodoAgent


class TranslatorAgent(KomodoAgent):
    shortcode = "translator"
    name = 'Translator Agent'
    purpose = 'Translates text'
    instructions = 'Please translate the following text to {}'

    def __init__(self, lang='French'):
        super().__init__(shortcode=self.shortcode + f"_{lang.lower()}",
                         name=self.name,
                         purpose=self.purpose,
                         instructions=self.instructions.format(lang))
