from .base import BobEndpoint


class Onboarding(BobEndpoint):
    @property
    def wizards(self):
        return Wizards(self.client)


class Wizards(BobEndpoint):
    def get(self):
        return self.client.get("onboarding/wizards")
