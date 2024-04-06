from faker import Faker


class FakerGenerator:
    """Generating fake values"""

    def __init__(self) -> None:
        self.faker = Faker()

    def generate_name(self):
        return self.faker.name()

    def generate_sentence(self, num_of_sentences: int = 1):
        return self.faker.paragraph(nb_sentences=num_of_sentences)

    def generate_title(self):
        return self.faker.company()
