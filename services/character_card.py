import re
from dataclasses import dataclass, field

IDENTITY_LABELS = {
    "Imię",
    "Nazwisko",
    "Rasa",
    "Klasa",
    "Profesja",
}

SECTION_LABELS = (
    "Umiejętności",
    "Zdolności",
    "Broń",
    "Pancerz",
    "Ekwipunek",
    "Monety",
    "Magia",
)

STAT_ABBREVIATIONS = {
    "ww",
    "us",
    "k",
    "odp",
    "zr",
    "int",
    "sw",
    "ogd",
    "a",
    "żyw",
    "s",
    "wt",
    "h",
    "sz",
    "mag",
    "po",
    "pp",
}

STAT_PATTERN = re.compile(
    r"\(([^()]+)\)\s*$"
)

STAT_VALUE_PATTERN = re.compile(
    r"^\s*(?P<base>-?\d+)"
    r"\s*(?:\+\s*(?P<development>-?\d+)\s*\^*)?"
    r"\s*(?:=\s*(?P<final>-?\d+))?\s*$"
)

MAGIC_ENTRY_PATTERN = re.compile(
    r"^\s*\[([^\]]+)\]\s*"
    r"\[([^\]]+)\]\s*"
    r"\[([^\]]+)\]\s*$"
)


@dataclass
class CharacterStat:
    name: str
    abbreviation: str
    value: str

    current_value: str

    base_value: str
    development_value: str
    final_value: str


@dataclass
class MagicEntry:
    name: str
    power_level: str
    casting_time: str


@dataclass
class CharacterCard:
    name: str
    surname: str = ""

    race: str = ""
    character_class: str = ""
    profession: str = ""

    profile_fields: list[tuple[str, str]] = field(
        default_factory=list
    )

    stats: list[CharacterStat] = field(
        default_factory=list
    )

    sections: dict[str, list[str]] = field(
        default_factory=dict
    )

    @property
    def full_name(self) -> str:
        return (
            f"{self.name} {self.surname}"
            .strip()
        )

    @property
    def subtitle_parts(self) -> list[str]:
        return [
            value
            for value in (
                self.race,
                self.character_class,
                self.profession,
            )
            if value
        ]

    def get_section(
            self,
            name: str,
    ) -> list[str]:
        return self.sections.get(
            name,
            [],
        )

    def get_magic_entries(
            self,
    ) -> list[MagicEntry]:
        return [
            _parse_magic_entry(value)
            for value
            in self.get_section("Magia")
        ]


def _extract_stat_abbreviation(
        label: str,
):
    match = STAT_PATTERN.search(label)

    if match is None:
        return None

    abbreviation = match.group(1).strip()

    if (
            abbreviation.casefold()
            not in STAT_ABBREVIATIONS
    ):
        return None

    return abbreviation


def _extract_current_value(
        value: str,
) -> str:
    if "=" not in value:
        return value

    current_value = value.rsplit(
        "=",
        1,
    )[-1].strip()

    return current_value or value


def _parse_stat_values(
        value: str,
) -> tuple[str, str, str]:
    normalized_value = (
        value
        .strip()
        .lstrip("*")
        .strip()
    )

    match = STAT_VALUE_PATTERN.fullmatch(
        normalized_value
    )

    if match is None:
        current_value = (
            _extract_current_value(
                normalized_value
            )
        )

        return (
            normalized_value,
            "—",
            current_value,
        )

    base_value = match.group(
        "base"
    )

    development_value = (
            match.group("development")
            or "0"
    )

    final_value = (
            match.group("final")
            or base_value
    )

    return (
        base_value,
        development_value,
        final_value,
    )


def _parse_magic_entry(
        value: str,
) -> MagicEntry:
    match = MAGIC_ENTRY_PATTERN.fullmatch(
        value
    )

    if match is None:
        return MagicEntry(
            name=value,
            power_level="—",
            casting_time="—",
        )

    return MagicEntry(
        name=match.group(1).strip(),
        power_level=match.group(2).strip(),
        casting_time=match.group(3).strip(),
    )


def _normalize_section(
        value,
) -> list[str]:
    if not value:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    normalized = str(value).strip()

    if not normalized:
        return []

    return [normalized]


def _normalize_profile_value(
        value,
) -> str:
    if isinstance(value, list):
        return ", ".join(
            str(item).strip()
            for item in value
            if str(item).strip()
        )

    return str(value).strip()


def build_character_card(
        character_data: dict,
) -> CharacterCard:
    card = CharacterCard(
        name=str(
            character_data.get(
                "Imię",
                "Nieznana postać",
            )
        ).strip(),

        surname=str(
            character_data.get(
                "Nazwisko",
                "",
            )
        ).strip(),

        race=str(
            character_data.get(
                "Rasa",
                "",
            )
        ).strip(),

        character_class=str(
            character_data.get(
                "Klasa",
                "",
            )
        ).strip(),

        profession=str(
            character_data.get(
                "Profesja",
                "",
            )
        ).strip(),
    )

    card.sections = {
        section_name: _normalize_section(
            character_data.get(
                section_name
            )
        )
        for section_name
        in SECTION_LABELS
    }

    for (
            label,
            raw_value,
    ) in character_data.items():

        if label in IDENTITY_LABELS:
            continue

        if label in SECTION_LABELS:
            continue

        value = _normalize_profile_value(
            raw_value
        )

        if not value:
            continue

        abbreviation = (
            _extract_stat_abbreviation(
                label
            )
        )

        if abbreviation is not None:
            (
                base_value,
                development_value,
                final_value,
            ) = _parse_stat_values(
                value
            )

            card.stats.append(
                CharacterStat(
                    name=label,
                    abbreviation=abbreviation,
                    value=value,

                    current_value=final_value,

                    base_value=base_value,
                    development_value=(
                        development_value
                    ),
                    final_value=final_value,
                )
            )

            continue

        card.profile_fields.append(
            (
                label,
                value,
            )
        )

    return card
