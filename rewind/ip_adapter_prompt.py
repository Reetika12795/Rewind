"""Utilities to build final prompt payload for IP Adapter image generation.

The goal is to combine structured prompt components into:
1. A high quality natural language prompt
2. A negative prompt string
3. A structured JSON payload (for logging or downstream automation)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class IPAdapterPromptPayload:
    """Structured payload representing all parts needed for generation."""
    core_prompt: str
    negative_prompt: str
    style_modifiers: List[str]
    architectural_details: List[str]
    atmospheric_elements: List[str]
    composition_guidance: List[str]
    historical_tags: List[str]

    def to_json(self) -> Dict[str, Any]:  # Ready for serialization
        return asdict(self)


class IPAdapterPromptBuilder:
    """Build final prompts from intermediate PromptComponents model."""

    def build(self, components) -> IPAdapterPromptPayload:  # components: PromptComponents
        base = components.core_description.strip()

        # Assemble an ordered list of fragments to keep prompt concise & rich
        fragments: List[str] = []
        if components.historical_style_tags:
            fragments.append(", ".join(components.historical_style_tags))
        if components.architectural_details:
            fragments.append(", ".join(components.architectural_details[:8]))
        if components.atmospheric_elements:
            fragments.append(", ".join(components.atmospheric_elements[:5]))
        if components.style_modifiers:
            fragments.append(", ".join(components.style_modifiers[:8]))
        if components.composition_guidance:
            fragments.append(", ".join(components.composition_guidance[:4]))

        combined = base
        for frag in fragments:
            if frag:
                combined += ", " + frag

        negative = ", ".join(components.negative_prompts) if components.negative_prompts else "modern elements, contemporary cars, modern signage, modern clothing"

        return IPAdapterPromptPayload(
            core_prompt=combined,
            negative_prompt=negative,
            style_modifiers=components.style_modifiers,
            architectural_details=components.architectural_details,
            atmospheric_elements=components.atmospheric_elements,
            composition_guidance=components.composition_guidance,
            historical_tags=components.historical_style_tags,
        )


__all__ = [
    "IPAdapterPromptBuilder",
    "IPAdapterPromptPayload",
]
