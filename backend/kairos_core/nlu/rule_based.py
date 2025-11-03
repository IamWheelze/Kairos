from __future__ import annotations

import re
from typing import Optional

from kairos_core.nlu.interfaces import NLUClient, NLUResult


class RuleBasedNLU(NLUClient):
    """Lightweight NLU for development and offline use.

    Heuristics map text to intents: NextSlide, PreviousSlide, ClearScreen, GoToSong.
    """

    async def detect_intent(self, text: str, context: Optional[dict] = None) -> NLUResult:
        t = (text or "").strip().lower()
        if not t:
            return NLUResult(intent="Fallback", params={}, confidence=0.0)

        # Clear screen
        if re.search(r"\b(clear|blank)( screen| lyrics)?\b", t):
            return NLUResult(intent="ClearScreen", params={}, confidence=0.9)

        # Next slide
        if re.search(r"\b(next)( slide)?\b", t):
            return NLUResult(intent="NextSlide", params={}, confidence=0.9)

        # Previous slide
        if re.search(r"\b(prev(ious)?|back)( slide)?\b", t):
            return NLUResult(intent="PreviousSlide", params={}, confidence=0.9)

        # Go to song by common patterns
        m = re.search(r"\b(show|go to|open|lyrics for)\s+(.+)$", t)
        if m:
            title = m.group(2).strip()
            # remove trailing polite words
            title = re.sub(r"\b(please|thanks)\b", "", title).strip()
            return NLUResult(intent="GoToSong", params={"song_title": title}, confidence=0.8)

        # Go to section
        m2 = re.search(r"\b(verse|chorus|bridge|tag|intro|outro)\s*(\d+)?\b", t)
        if m2:
            sec = m2.group(0)
            return NLUResult(intent="GoToSection", params={"section": sec}, confidence=0.8)

        # Play/pause
        if re.search(r"\b(play|pause|resume)( media| video| audio)?\b", t):
            return NLUResult(intent="PlayPauseMedia", params={}, confidence=0.8)

        return NLUResult(intent="Fallback", params={}, confidence=0.0)
