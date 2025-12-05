"""
vmix_api_types.py
------------------
Datatyper som representerar vMix API-data.

Används av vmix_client.py för att:
 • returnera strukturer istället för rå XML
 • göra projektet stabilt, typat och lätt att felsöka
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List


# ------------------------------------------------------------
# Grundstrukturer
# ------------------------------------------------------------

@dataclass
class VMixTextField:
    """Ett textfält i ett GT/Title input"""
    name: str
    value: str = ""


@dataclass
class VMixImageField:
    """Ett bildfält (*.Source) i GT/Title"""
    name: str
    source: str = ""


@dataclass
class VMixInput:
    """Representerar ett <input> från vMix XML API"""

    number: int
    key: str
    title: str
    short_title: str
    type: str

    # Innehåll
    text_fields: List[VMixTextField] = field(default_factory=list)
    image_fields: List[VMixImageField] = field(default_factory=list)

    def get_text(self, name: str) -> str:
        for t in self.text_fields:
            if t.name == name:
                return t.value
        return ""

    def get_image(self, name: str) -> str:
        for i in self.image_fields:
            if i.name == name:
                return i.source
        return ""


@dataclass
class VMixState:
    """Root-struktur för hela API-svaret"""
    version: str
    edition: str
    preset: str
    inputs: List[VMixInput] = field(default_factory=list)

    def find_input_by_number(self, number: int) -> Optional[VMixInput]:
        for inp in self.inputs:
            if inp.number == number:
                return inp
        return None

    def find_input(self, name_or_number: str | int) -> Optional[VMixInput]:
        """Tillåter sökning via nummer, namn eller shortTitle"""
        if isinstance(name_or_number, int):
            return self.find_input_by_number(name_or_number)

        name = str(name_or_number).strip().lower()

        # matcha på title eller short_title
        for inp in self.inputs:
            if inp.title.lower() == name or inp.short_title.lower() == name:
                return inp
        return None
