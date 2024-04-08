from enum import Enum


class Komodo:
    company = "Komodo AI"


class KomodoApplianceType(Enum):
    enterprise = "enterprise"
    retail = "retail"


class KomodoFeatures(Enum):
    chat = "chat"
    chatdoc = "chatdoc"
    reportbuilder = "reportbuilder"


if __name__ == '__main__':
    print(KomodoApplianceType.enterprise.name)
    features = [e.value for e in KomodoFeatures]
    print(", ".join(features))
