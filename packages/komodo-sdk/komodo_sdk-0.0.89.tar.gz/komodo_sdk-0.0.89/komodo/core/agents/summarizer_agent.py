from komodo.framework.komodo_agent import KomodoAgent


class SummarizerAgent(KomodoAgent):
    shortcode = "summarizer"
    name = 'Summary Agent'
    purpose = 'Summarize text'
    instructions = 'Please summarize the following text in {} words'

    def __init__(self, n=50):
        super().__init__(shortcode=self.shortcode + f"_{n}",
                         name=self.name,
                         purpose=self.purpose,
                         instructions=self.instructions.format(n))

    @classmethod
    def create(cls, n=50):
        return KomodoAgent(shortcode=cls.shortcode,
                           name=cls.name,
                           purpose=cls.purpose,
                           instructions=cls.instructions.format(n))


if __name__ == "__main__":
    summarizer = SummarizerAgent.create()
    print(summarizer)
