"""Rewind Analysis Agents (clean rebuild)

Provides resilient data models and an agent that can operate in two modes:
- Heuristic (PROMPT_ONLY or no API key)
- OpenAI-assisted (vision + text models) with optional Wikipedia enrichment
"""

from __future__ import annotations

import base64
import json
from io import BytesIO
from typing import List, Optional

from PIL import Image
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from .config import Config
from .wiki import contextual_wiki_lookup


# ---------------- Data Models ---------------- #
class AnalysisResult(BaseModel):
    architectural_elements: List[str] = Field(default_factory=list)
    clothing_fashion: List[str] = Field(default_factory=list)
    vehicles_transportation: List[str] = Field(default_factory=list)
    technology_visible: List[str] = Field(default_factory=list)
    materials_construction: List[str] = Field(default_factory=list)

    scene_type: str = "unknown"
    lighting_conditions: str = "unknown"
    weather_atmosphere: str = "unknown"
    time_of_day: str = "unknown"
    season: str = "unknown"

    architectural_style_research: List[str] = Field(default_factory=list)
    cultural_context_needed: List[str] = Field(default_factory=list)
    fashion_period_research: List[str] = Field(default_factory=list)
    technology_evolution: List[str] = Field(default_factory=list)

    visual_style_descriptors: List[str] = Field(default_factory=list)
    composition_elements: List[str] = Field(default_factory=list)
    color_palette_notes: List[str] = Field(default_factory=list)

    clarification_questions: List[str] = Field(default_factory=list)
    research_suggestions: List[str] = Field(default_factory=list)


class HistoricalContext(BaseModel):
    architectural_styles: List[str] = Field(default_factory=list)
    common_materials: List[str] = Field(default_factory=list)
    typical_clothing: List[str] = Field(default_factory=list)
    transportation_methods: List[str] = Field(default_factory=list)
    technology_level: List[str] = Field(default_factory=list)
    cultural_characteristics: List[str] = Field(default_factory=list)
    notable_events: List[str] = Field(default_factory=list)
    social_context: List[str] = Field(default_factory=list)


class PromptComponents(BaseModel):
    core_description: str = ""
    historical_style_tags: List[str] = Field(default_factory=list)
    architectural_details: List[str] = Field(default_factory=list)
    atmospheric_elements: List[str] = Field(default_factory=list)
    negative_prompts: List[str] = Field(default_factory=list)
    style_modifiers: List[str] = Field(default_factory=list)
    composition_guidance: List[str] = Field(default_factory=list)


# ---------------- Agent ---------------- #
class RewindAnalysisAgent:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.client: Optional[OpenAI] = None
        if self.config.openai_api_key and not self.config.prompt_only:
            try:
                self.client = OpenAI(api_key=self.config.openai_api_key)
            except Exception as e:
                print(f"Failed to init OpenAI client: {e}")
                self.client = None

    # -------- Image Analysis -------- #
    async def analyze_image(self, image: Image.Image, location: str, target_year: int) -> AnalysisResult:
        if self.config.prompt_only or not self.client:
            return self._fallback_analysis(location, target_year)
        try:
            buf = BytesIO(); image.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            instruction = (
                "Return ONLY JSON with keys: architectural_elements, vehicles_transportation, technology_visible, "
                "scene_type, lighting_conditions, weather_atmosphere, time_of_day, season, composition_elements."
            )
            resp = self.client.chat.completions.create(
                model=self.config.vision_model,
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                        {"type": "text", "text": f"Location: {location}; TargetYear: {target_year}"}
                    ]}
                ],
                max_tokens=700,
                temperature=0.3
            )
            raw = resp.choices[0].message.content or ""
            first = raw.find('{'); last = raw.rfind('}')
            blob = raw[first:last+1] if first != -1 and last != -1 else raw
            try:
                data = json.loads(blob)
            except Exception:
                return self._fallback_analysis(location, target_year)
            if isinstance(data, dict) and 'AnalysisResult' in data and isinstance(data['AnalysisResult'], dict):
                data = data['AnalysisResult']
            if not isinstance(data, dict):
                return self._fallback_analysis(location, target_year)
            list_fields = [
                'architectural_elements','clothing_fashion','vehicles_transportation','technology_visible','materials_construction',
                'architectural_style_research','cultural_context_needed','fashion_period_research','technology_evolution',
                'visual_style_descriptors','composition_elements','color_palette_notes','clarification_questions','research_suggestions'
            ]
            for lf in list_fields:
                val = data.get(lf)
                if val is None:
                    data[lf] = []
                elif isinstance(val, str):
                    data[lf] = [p.strip() for p in val.split(',') if p.strip()]
                elif not isinstance(val, list):
                    data[lf] = []
            for sf in ['scene_type','lighting_conditions','weather_atmosphere','time_of_day','season']:
                if not isinstance(data.get(sf), str):
                    data[sf] = 'unknown'
            try:
                return AnalysisResult(**data)
            except ValidationError:
                return self._fallback_analysis(location, target_year)
        except Exception as e:
            print(f"Error in image analysis: {e}")
            return self._error_analysis(str(e))

    # -------- Historical Context -------- #
    async def get_historical_context(self, location: str, target_year: int, analysis: AnalysisResult) -> HistoricalContext:
        if self.config.prompt_only or not self.client:
            return self._fallback_context(location, target_year)
        prompt = (
            f"Provide ONLY JSON for HistoricalContext about {location} in {target_year}. "
            f"Image cues: {', '.join(analysis.architectural_elements[:8])}; Scene: {analysis.scene_type}. "
            "Arrays only, [] if unknown."
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.config.text_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.35
            )
            raw = resp.choices[0].message.content or ""
            first = raw.find('{'); last = raw.rfind('}')
            blob = raw[first:last+1] if first != -1 and last != -1 else raw
            try:
                data = json.loads(blob)
            except Exception:
                return self._fallback_context(location, target_year)
            if isinstance(data, dict) and 'HistoricalContext' in data:
                data = data['HistoricalContext']
            if not isinstance(data, dict):
                return self._fallback_context(location, target_year)
            list_fields = [
                'architectural_styles','common_materials','typical_clothing','transportation_methods','technology_level',
                'cultural_characteristics','notable_events','social_context'
            ]
            for lf in list_fields:
                val = data.get(lf)
                if val is None:
                    data[lf] = []
                elif isinstance(val, str):
                    data[lf] = [s.strip() for s in val.split(',') if s.strip()]
                elif not isinstance(val, list):
                    data[lf] = []
            try:
                return HistoricalContext(**data)
            except ValidationError:
                return self._fallback_context(location, target_year)
        except Exception as e:
            print(f"Error getting historical context: {e}")
            return self._error_context(str(e))

    # -------- Prompt Components -------- #
    async def generate_prompt_components(self, analysis: AnalysisResult, context: HistoricalContext, location: str, target_year: int) -> PromptComponents:
        def _dedupe(seq: List[str]) -> List[str]:
            seen=set(); out=[]
            for s in seq:
                k=s.lower().strip()
                if k and k not in seen:
                    seen.add(k); out.append(s)
            return out
        def _short(s: Optional[str]) -> str:
            return (s or '').strip().lower()[:60]
        arch = analysis.architectural_elements or []
        styles = context.architectural_styles or []
        mats = context.common_materials or []
        mood = [analysis.lighting_conditions, analysis.weather_atmosphere, analysis.time_of_day, analysis.season]
        wiki_terms: List[str] = []
        if self.config.enable_wiki and location:
            try:
                wiki_data = contextual_wiki_lookup(location, target_year, styles)
                for r in wiki_data.get("results", [])[:3]:
                    summary=(r.get("summary") or "")[:400]
                    for tok in summary.split():
                        t=tok.strip('.,;:"()').lower()
                        if 3 <= len(t) <= 15 and t.isalpha() and t not in wiki_terms:
                            wiki_terms.append(t)
                        if len(wiki_terms) >= 15: break
                    if len(wiki_terms) >= 15: break
            except Exception:
                pass
        base_neg = ["modern cars","neon lights","modern signage","skyscrapers","contemporary clothing","smartphones","electric poles","traffic lights"]
        if analysis.technology_visible:
            base_neg.extend([f"modern {t}" for t in analysis.technology_visible[:5]])
        base_neg=_dedupe(base_neg)[:15]
        def build_core():
            scene=analysis.scene_type if analysis.scene_type!='unknown' else 'scene'
            return f"{target_year} {location} {scene}".strip()
        def heuristic():
            return PromptComponents(
                core_description=build_core(),
                historical_style_tags=_dedupe([*styles[:8],*mats[:5],*wiki_terms[:6]])[:10],
                architectural_details=_dedupe([*arch[:10],*mats[:5]])[:12],
                atmospheric_elements=_dedupe([_short(x) for x in mood if x and x!='unknown'])[:6],
                negative_prompts=base_neg,
                style_modifiers=["historical realism","rich texture","fine detail","natural lighting","film grain","high dynamic range"],
                composition_guidance=_dedupe([*(analysis.composition_elements[:4] if analysis.composition_elements else []),"maintain original perspective"])[:5]
            )
        if self.config.prompt_only or not self.client:
            return heuristic()
        prompt_text=(
            "You are a prompt engineering assistant. Produce ONLY compact JSON (no markdown)."\
            f" Target: transform scene to {location} in {target_year}."\
            " Keys: core_description (<=40 words), historical_style_tags (5-10), architectural_details (6-12),"\
            " atmospheric_elements (4-8), negative_prompts (8-15), style_modifiers (6-10), composition_guidance (3-6)."\
            " Avoid commentary.\n"\
            f"SceneType={analysis.scene_type}; Arch={'; '.join(arch[:10])}; Styles={'; '.join(styles[:8])}; "\
            f"Materials={'; '.join(mats[:6])}; Mood={'; '.join([m for m in mood if m and m!='unknown'][:4])}."\
        )
        if wiki_terms:
            prompt_text += " ExtraHistoricalKeywords="+", ".join(wiki_terms[:12])
        try:
            resp=self.client.chat.completions.create(
                model=self.config.text_model,
                messages=[{"role":"user","content":prompt_text}],
                max_tokens=750,
                temperature=0.4
            )
            raw=(resp.choices[0].message.content or '').strip()
            first=raw.find('{'); last=raw.rfind('}')
            if first!=-1 and last!=-1:
                raw=raw[first:last+1]
            try:
                data=json.loads(raw)
            except Exception:
                return heuristic()
            if not isinstance(data, dict):
                return heuristic()
            for key in ["historical_style_tags","architectural_details","atmospheric_elements","negative_prompts","style_modifiers","composition_guidance"]:
                val=data.get(key)
                if isinstance(val,str):
                    data[key]=[p.strip() for p in val.split(',') if p.strip()]
                elif not isinstance(val,list):
                    data[key]=[]
            data.setdefault('core_description', build_core())
            try:
                return PromptComponents(**data)
            except ValidationError:
                return heuristic()
        except Exception as e:
            print(f"Error generating prompt components: {e}")
            return heuristic()

    # -------- Fallback & Error helpers -------- #
    def _fallback_analysis(self, location: str, target_year: int) -> AnalysisResult:
        return AnalysisResult(
            architectural_elements=["buildings","structures"],
            vehicles_transportation=["cars"],
            technology_visible=["modern tech"],
            scene_type="urban scene",
            lighting_conditions="daylight",
            weather_atmosphere="clear",
            time_of_day="daytime",
            season="unknown",
            composition_elements=["maintain original composition"],
            clarification_questions=["Key architectural style details?"],
            research_suggestions=["Research local period architecture"]
        )
    def _fallback_context(self, location: str, target_year: int) -> HistoricalContext:
        return HistoricalContext(
            architectural_styles=[f"{target_year} period architecture"],
            common_materials=["stone","wood","brick"],
            transportation_methods=["walking","horse-drawn"],
            technology_level=[f"{target_year} technology"],
            cultural_characteristics=[f"{target_year} culture"],
            notable_events=[f"Events around {target_year}"],
            social_context=[f"{target_year} social context"]
        )
    def _error_analysis(self, error: str) -> AnalysisResult:
        return AnalysisResult(clarification_questions=[f"Error: {error}"])
    def _error_context(self, error: str) -> HistoricalContext:
        return HistoricalContext(social_context=[f"Error: {error}"])
    def _error_prompts(self, error: str) -> PromptComponents:
        return PromptComponents(core_description=f"Error generating prompts: {error}")