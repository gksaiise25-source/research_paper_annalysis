"""
Grammar and Language Analysis Module - Checks academic writing quality.
"""
import re
from typing import Dict, List
from loguru import logger


class GrammarAnalyser:

    # Passive voice indicators
    PASSIVE_PATTERNS = [
        r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
        r'\b(has|have|had)\s+been\s+\w+ed\b',
    ]

    # Wordy phrases and their concise alternatives
    WORDY_PHRASES = {
        "due to the fact that": "because",
        "in order to": "to",
        "at this point in time": "now",
        "it is important to note that": "",
        "it should be noted that": "",
        "in the event that": "if",
        "with the exception of": "except",
        "in spite of the fact that": "although",
        "for the purpose of": "for",
        "in the near future": "soon",
        "a number of": "several",
        "the majority of": "most",
        "in close proximity to": "near",
        "at the present time": "currently",
        "in the process of": "during",
        "subsequent to": "after",
        "prior to": "before",
        "with regard to": "regarding",
        "with respect to": "regarding",
        "in terms of": "for",
        "make use of": "use",
        "are able to": "can",
        "is capable of": "can",
        "it is worth noting": "",
        "needless to say": "",
        "it goes without saying": "",
    }

    # Hedging language (good in academia)
    HEDGING_WORDS = ["may", "might", "could", "suggest", "indicate", "appear", "seem", "likely"]

    # Non-academic informal words
    INFORMAL_WORDS = {
        "a lot": "many / significantly",
        "very": "highly / substantially",
        "really": "substantially",
        "got": "obtained / achieved",
        "big": "large / significant",
        "small": "limited / minor",
        "show": "demonstrate / indicate",
        "use": "utilise / employ",
        "find": "identify / determine",
        "look at": "examine / investigate",
        "check": "verify / validate",
        "stuff": "components / elements",
        "things": "aspects / factors",
        "good": "effective / promising",
        "bad": "poor / ineffective",
        "get": "obtain / acquire",
        "make": "construct / develop",
        "do": "perform / conduct",
    }

    # Repeated word detection threshold
    REPEAT_THRESHOLD = 5

    def analyse(self, extracted_content: Dict) -> Dict:
        """Perform grammar and language quality analysis."""
        full_text = extracted_content.get("full_text", "")
        abstract = extracted_content.get("abstract", "")
        introduction = extracted_content.get("introduction", "")

        if not full_text:
            return {"error": "No text available for grammar analysis."}

        # Sample sections for analysis (not entire document, for performance)
        sample_text = f"{abstract}\n\n{introduction}"
        if len(sample_text) < 500:
            sample_text = full_text[:5000]
        else:
            sample_text = sample_text[:5000]

        suggestions = []

        # Check wordy phrases
        wordy_suggestions = self._check_wordy_phrases(sample_text)
        suggestions.extend(wordy_suggestions)

        # Check informal language
        informal_suggestions = self._check_informal_language(sample_text)
        suggestions.extend(informal_suggestions)

        # Check passive voice overuse
        passive_issues = self._check_passive_voice(sample_text)
        suggestions.extend(passive_issues)

        # Check sentence length
        length_issues = self._check_sentence_length(sample_text)
        suggestions.extend(length_issues)

        # Check repeated words
        repeat_issues = self._check_word_repetition(full_text)
        suggestions.extend(repeat_issues)

        # Readability score (Flesch-Kincaid approximation)
        readability = self._compute_readability(sample_text)

        # Academic tone score
        tone_score = self._assess_academic_tone(full_text)

        total_issues = len(suggestions)
        score = max(0, 100 - (total_issues * 3))

        return {
            "grammar_score": round(score, 1),
            "readability_score": readability,
            "academic_tone_score": round(tone_score, 1),
            "total_suggestions": total_issues,
            "suggestions": suggestions[:30],
            "summary": {
                "wordy_phrases_found": len(wordy_suggestions),
                "informal_words_found": len(informal_suggestions),
                "passive_voice_issues": len(passive_issues),
                "sentence_length_issues": len(length_issues),
                "repeated_words": len(repeat_issues),
            },
            "recommendations": self._generate_recommendations(
                total_issues, readability, tone_score
            ),
        }

    def _check_wordy_phrases(self, text: str) -> List[Dict]:
        suggestions = []
        text_lower = text.lower()
        for phrase, replacement in self.WORDY_PHRASES.items():
            if phrase in text_lower:
                suggestion = {
                    "type": "wordy_phrase",
                    "original": phrase,
                    "suggestion": replacement if replacement else f"(remove or rephrase)",
                    "reason": "Wordy expression reduces clarity in academic writing.",
                    "severity": "minor",
                }
                suggestions.append(suggestion)
        return suggestions

    def _check_informal_language(self, text: str) -> List[Dict]:
        suggestions = []
        sentences = re.split(r'[.!?]', text)
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            for informal, formal in self.INFORMAL_WORDS.items():
                if re.search(r'\b' + re.escape(informal) + r'\b', sentence_lower):
                    suggestions.append({
                        "type": "informal_language",
                        "original": sentence.strip()[:100],
                        "suggestion": f"Replace '{informal}' with '{formal}'",
                        "reason": "Academic writing requires formal vocabulary.",
                        "severity": "minor",
                    })
                    break  # One suggestion per sentence
        return suggestions[:10]

    def _check_passive_voice(self, text: str) -> List[Dict]:
        suggestions = []
        sentences = re.split(r'[.!?]', text)
        passive_count = 0
        for sentence in sentences:
            for pattern in self.PASSIVE_PATTERNS:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_count += 1
                    break

        if len(sentences) > 0:
            passive_ratio = passive_count / len(sentences)
            if passive_ratio > 0.4:
                suggestions.append({
                    "type": "passive_voice_overuse",
                    "original": f"~{int(passive_ratio*100)}% of sentences use passive voice",
                    "suggestion": "Vary sentence construction with more active voice.",
                    "reason": "Excessive passive voice can reduce clarity and engagement.",
                    "severity": "moderate",
                })
        return suggestions

    def _check_sentence_length(self, text: str) -> List[Dict]:
        suggestions = []
        sentences = re.split(r'[.!?]', text)
        long_sentences = []
        for sent in sentences:
            words = sent.split()
            if len(words) > 45:
                long_sentences.append(sent.strip()[:120] + "...")

        if long_sentences:
            suggestions.append({
                "type": "long_sentences",
                "original": long_sentences[0] if long_sentences else "",
                "suggestion": "Break sentences longer than 40 words into shorter, clearer sentences.",
                "reason": f"{len(long_sentences)} overly long sentence(s) detected. These may reduce readability.",
                "severity": "moderate",
            })
        return suggestions

    def _check_word_repetition(self, text: str) -> List[Dict]:
        suggestions = []
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        from collections import Counter
        word_counts = Counter(words)

        stop_words = {
            "that", "this", "with", "have", "from", "they", "been",
            "were", "their", "which", "will", "each", "also", "than",
            "when", "more", "used", "such", "into", "these", "using",
            "data", "paper", "study", "research", "results", "approach",
            "method", "proposed", "model", "based", "show"
        }

        repeated = [
            (word, count) for word, count in word_counts.most_common(30)
            if count > self.REPEAT_THRESHOLD and word not in stop_words
        ]

        for word, count in repeated[:5]:
            suggestions.append({
                "type": "word_repetition",
                "original": f"'{word}' repeated {count} times",
                "suggestion": f"Consider using synonyms for '{word}' to improve variety.",
                "reason": "Excessive repetition reduces writing quality.",
                "severity": "minor",
            })

        return suggestions

    def _compute_readability(self, text: str) -> Dict:
        """Approximate Flesch-Kincaid readability."""
        sentences = re.split(r'[.!?]', text)
        sentences = [s for s in sentences if s.strip()]
        words = text.split()
        syllables = sum(self._count_syllables(w) for w in words)

        if not sentences or not words:
            return {"score": None, "level": "Unknown"}

        asl = len(words) / len(sentences)  # Avg sentence length
        asw = syllables / len(words)  # Avg syllables per word

        fk_score = 206.835 - 1.015 * asl - 84.6 * asw
        fk_score = max(0, min(100, fk_score))

        if fk_score >= 70:
            level = "Easy"
        elif fk_score >= 50:
            level = "Standard"
        elif fk_score >= 30:
            level = "Difficult (Academic)"
        else:
            level = "Very Difficult"

        return {"score": round(fk_score, 1), "level": level}

    def _count_syllables(self, word: str) -> int:
        word = word.lower().strip(".,!?;:")
        if len(word) <= 3:
            return 1
        count = len(re.findall(r'[aeiou]+', word))
        if word.endswith('e'):
            count -= 1
        return max(1, count)

    def _assess_academic_tone(self, text: str) -> float:
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)
        if total_words == 0:
            return 50.0

        # Score based on hedging, formal vocabulary
        hedging_count = sum(1 for w in words if w in self.HEDGING_WORDS)
        informal_count = sum(1 for phrase in self.INFORMAL_WORDS for w in [phrase.split()[0]] if w in words)

        score = 70 + (hedging_count / total_words * 500) - (informal_count / total_words * 300)
        return min(100, max(20, score))

    def _generate_recommendations(
        self, total_issues: int, readability: Dict, tone_score: float
    ) -> List[str]:
        recs = []
        if total_issues > 15:
            recs.append("Significant language improvements required before submission.")
        elif total_issues > 7:
            recs.append("Moderate language improvements recommended.")
        else:
            recs.append("Language quality is acceptable. Minor improvements suggested.")

        if readability.get("score") and readability["score"] < 30:
            recs.append("Improve readability by shortening sentences and using simpler phrasing.")
        if tone_score < 60:
            recs.append("Strengthen academic tone by using formal vocabulary and hedging language.")
        recs.append("Use a professional grammar tool (e.g., Grammarly Academic) for a final review before submission.")
        return recs
