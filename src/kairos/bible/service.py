"""Bible verse lookup service.

Supports multiple Bible APIs:
- bible-api.com (default, free, no API key)
- bible.helloao.org (1000+ translations, free, no API key)
"""

import re
from typing import Optional, Dict, List, Tuple
from kairos.logging import get_logger

log = get_logger("kairos.bible.service")

# Try to import requests, but make it optional
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    log.warning("requests library not available. Bible features will be disabled.")


class BibleVerse:
    """Represents a Bible verse or passage."""

    def __init__(
        self,
        reference: str,
        text: str,
        translation: str = "KJV",
        verses: Optional[List[Dict]] = None
    ):
        self.reference = reference
        self.text = text
        self.translation = translation
        self.verses = verses or []

    def __str__(self):
        return f"{self.reference} ({self.translation})\n{self.text}"

    def to_dict(self):
        return {
            "reference": self.reference,
            "text": self.text,
            "translation": self.translation,
            "verses": self.verses
        }


class BibleService:
    """Service for fetching Bible verses from various APIs."""

    # Supported APIs
    BIBLE_API_COM = "bible-api.com"
    BIBLE_HELLO_AO = "bible.helloao.org"

    # Translation mappings
    TRANSLATION_ALIASES = {
        "kjv": "KJV",
        "esv": "ESV",
        "niv": "NIV",
        "nlt": "NLT",
        "nasb": "NASB",
        "nkjv": "NKJV",
        "web": "web",  # World English Bible
        "clementine": "clementine",  # Latin Vulgate
    }

    def __init__(self, api: str = BIBLE_API_COM, default_translation: str = "KJV"):
        """Initialize Bible service.

        Args:
            api: Which API to use (default: bible-api.com)
            default_translation: Default Bible translation (default: KJV)
        """
        self.api = api
        self.default_translation = default_translation
        self.session = None

        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": "Kairos-Voice-Control/1.0"
            })
        else:
            log.error("Cannot initialize BibleService: requests library not installed")

    def is_available(self) -> bool:
        """Check if Bible service is available."""
        return REQUESTS_AVAILABLE and self.session is not None

    def parse_reference(self, reference: str) -> Optional[Tuple[str, int, int, Optional[int]]]:
        """Parse a Bible reference into components.

        Args:
            reference: Bible reference like "John 3:16" or "Genesis 1:1-3"

        Returns:
            Tuple of (book, chapter, start_verse, end_verse) or None if invalid
        """
        # Normalize reference
        reference = reference.strip()

        # Pattern: Book Chapter:Verse or Book Chapter:Verse-Verse
        pattern = r"^(\d?\s*[A-Za-z]+)\s+(\d+):(\d+)(?:-(\d+))?$"
        match = re.match(pattern, reference, re.IGNORECASE)

        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            start_verse = int(match.group(3))
            end_verse = int(match.group(4)) if match.group(4) else None
            return (book, chapter, start_verse, end_verse)

        # Pattern: Book Chapter (entire chapter)
        pattern_chapter = r"^(\d?\s*[A-Za-z]+)\s+(\d+)$"
        match_chapter = re.match(pattern_chapter, reference, re.IGNORECASE)

        if match_chapter:
            book = match_chapter.group(1).strip()
            chapter = int(match_chapter.group(2))
            return (book, chapter, 1, None)  # Will fetch entire chapter

        return None

    def get_verse(
        self,
        reference: str,
        translation: Optional[str] = None
    ) -> Optional[BibleVerse]:
        """Fetch a Bible verse or passage.

        Args:
            reference: Bible reference (e.g., "John 3:16", "Genesis 1:1-3")
            translation: Bible translation (default: self.default_translation)

        Returns:
            BibleVerse object or None if not found
        """
        if not self.is_available():
            log.error("Bible service not available: requests library not installed")
            return None

        translation = translation or self.default_translation
        translation = self.TRANSLATION_ALIASES.get(translation.lower(), translation)

        log.info(f"Fetching Bible verse: {reference} ({translation})")

        try:
            if self.api == self.BIBLE_API_COM:
                return self._fetch_from_bible_api_com(reference, translation)
            elif self.api == self.BIBLE_HELLO_AO:
                return self._fetch_from_bible_hello_ao(reference, translation)
            else:
                log.error(f"Unsupported Bible API: {self.api}")
                return None
        except Exception as e:
            log.error(f"Error fetching Bible verse: {e}")
            return None

    def _fetch_from_bible_api_com(
        self,
        reference: str,
        translation: str
    ) -> Optional[BibleVerse]:
        """Fetch verse from bible-api.com.

        Supports: KJV (default), web, clementine, and custom translations
        Rate limit: 15 requests per 30 seconds
        """
        try:
            # bible-api.com format: GET /reference?translation=version
            url = f"https://bible-api.com/{reference}"
            params = {}

            if translation.lower() != "kjv":
                params["translation"] = translation.lower()

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                return BibleVerse(
                    reference=data.get("reference", reference),
                    text=data.get("text", "").strip(),
                    translation=data.get("translation_id", translation).upper(),
                    verses=data.get("verses", [])
                )
            elif response.status_code == 404:
                log.warning(f"Verse not found: {reference}")
                return None
            else:
                log.error(f"Bible API error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            log.error(f"Network error fetching verse: {e}")
            return None

    def _fetch_from_bible_hello_ao(
        self,
        reference: str,
        translation: str
    ) -> Optional[BibleVerse]:
        """Fetch verse from bible.helloao.org.

        Supports 1000+ translations
        No rate limits
        """
        try:
            # Parse reference to get components
            parsed = self.parse_reference(reference)
            if not parsed:
                log.error(f"Invalid reference format: {reference}")
                return None

            book, chapter, start_verse, end_verse = parsed

            # bible.helloao.org format is different - needs specific translation ID
            # For now, fall back to bible-api.com
            log.warning("bible.helloao.org not yet fully implemented, using bible-api.com")
            return self._fetch_from_bible_api_com(reference, translation)

        except Exception as e:
            log.error(f"Error fetching from bible.helloao.org: {e}")
            return None

    def search_verses(
        self,
        query: str,
        translation: Optional[str] = None,
        limit: int = 10
    ) -> List[BibleVerse]:
        """Search for verses containing specific text.

        Note: Not all APIs support search. This is a future enhancement.

        Args:
            query: Search query
            translation: Bible translation
            limit: Maximum results

        Returns:
            List of matching BibleVerse objects
        """
        log.warning("Bible verse search not yet implemented")
        return []

    def get_verse_of_the_day(
        self,
        translation: Optional[str] = None
    ) -> Optional[BibleVerse]:
        """Get the verse of the day.

        Note: Not all APIs provide this. This is a future enhancement.

        Args:
            translation: Bible translation

        Returns:
            BibleVerse object or None
        """
        log.warning("Verse of the day not yet implemented")
        return None

    def get_supported_translations(self) -> List[str]:
        """Get list of supported Bible translations.

        Returns:
            List of translation abbreviations
        """
        if self.api == self.BIBLE_API_COM:
            return ["KJV", "WEB", "CLEMENTINE"]
        elif self.api == self.BIBLE_HELLO_AO:
            # Supports 1000+ but we'll list common ones
            return ["KJV", "ESV", "NIV", "NLT", "NASB", "NKJV", "WEB"]
        return ["KJV"]
