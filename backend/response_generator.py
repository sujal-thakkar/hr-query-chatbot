# backend/response_generator.py
from typing import List, Dict, Any
from ai_client import AIClientManager
from shared_models import SearchResult
from cache import get_cache
from config import AI_SUMMARY_CACHE_TTL_SECONDS

class ResponseGenerator:
    """Handles the generation of AI and fallback responses."""

    def __init__(self, ai_client: AIClientManager):
        self.ai_client = ai_client
        self._summary_cache = get_cache(prefix="ai:summary", default_ttl=AI_SUMMARY_CACHE_TTL_SECONDS)

    def generate_response(self, query: str, search_results: List[SearchResult]) -> Dict[str, Any]:
        """Generates a response dictionary containing candidates and a message."""
        top_candidates = self._prepare_candidate_data(search_results)

        if not top_candidates:
            message = self._get_no_candidates_message()
            return {"candidates": [], "message": message}

        if self.ai_client and self.ai_client.is_available():
            try:
                # Cache key derived from query + top candidate IDs/names
                cache_key = self._summary_cache_key(query, top_candidates)
                cached = self._summary_cache.get(cache_key)
                if cached:
                    return {"candidates": top_candidates, "message": cached}

                ai_message = self._generate_ai_summary(query, top_candidates)
                try:
                    self._summary_cache.set(cache_key, ai_message)
                except Exception:
                    pass
                return {"candidates": top_candidates, "message": ai_message}
            except Exception as e:
                print(f"AI generation failed: {e}. Using enhanced fallback.")
                fallback_message = self._get_enhanced_fallback_message(top_candidates)
                return {"candidates": top_candidates, "message": fallback_message}
        else:
            fallback_message = self._get_enhanced_fallback_message(top_candidates)
            return {"candidates": top_candidates, "message": fallback_message}

    def _prepare_candidate_data(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Converts SearchResult objects to dictionaries for the API response."""
        candidates = []
        for result in search_results:
            # result.employee may be Pydantic model or dict-like
            employee_dict = result.employee if isinstance(result.employee, dict) else result.employee.dict()
            candidate_data = dict(employee_dict)
            candidate_data['final_score'] = result.relevance_score
            candidate_data['match_reasons'] = result.match_reasons
            candidate_data['confidence'] = result.confidence
            candidates.append(candidate_data)
        return candidates

    def _generate_ai_summary(self, query: str, top_candidates: List[Dict[str, Any]]) -> str:
        """Generates a conversational summary using the AI client."""
        system_prompt = (
            "You are an expert HR consultant. Your responses should be conversational, "
            "specific about why each candidate fits the role, highlight unique strengths, "
            "and end with a helpful next step. Format your response as a cohesive narrative."
        )

        context = self._build_ai_context(top_candidates)
        user_prompt = f'''User Query: "{query}"

Candidate Information:
{context}

Please provide a comprehensive summary of the top candidates based on the user's query.'''

        return self.ai_client.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=800,
            temperature=0.7
        )

    def _build_ai_context(self, top_candidates: List[Dict[str, Any]]) -> str:
        """Builds the detailed context string for the AI prompt."""
        context_parts = []
        for i, candidate in enumerate(top_candidates, 1):
            skills = ", ".join(candidate.get('skills', [])[:12])
            projects = ", ".join(candidate.get('projects', [])[:6])
            reasons = "; ".join(candidate.get('match_reasons', [])[:5])
            score = candidate.get('final_score', 0.0)
            desc = (
                f"Candidate {i}: {candidate.get('name')}\n"
                f"Experience: {candidate.get('experience_years')} years | Match Score: {score:.2f}\n"
                f"Skills: {skills}\n"
                f"Projects: {projects}\n"
                f"Why they fit: {reasons}"
            )
            context_parts.append(desc)
        return "\n\n".join(context_parts)

    def _get_enhanced_fallback_message(self, top_candidates: List[Dict[str, Any]]) -> str:
        """Generates a detailed, formatted fallback message when AI is unavailable."""
        count = len(top_candidates)
        lines = [f"I've identified {count} candidate{'s' if count != 1 else ''} for your requirements:\n"]
        for i, c in enumerate(top_candidates, 1):
            score = c.get('final_score', 0.0)
            lines.append(f"{i}. {c.get('name')} - {c.get('experience_years')} years (Score: {score:.2f})")
            lines.append(f"   - Skills: {', '.join(c.get('skills', [])[:12])}")
            reasons = c.get('match_reasons')
            if reasons:
                lines.append(f"   - Match Reasons: {'; '.join(reasons[:5])}")
        lines.append("\nWould you like more specific information about any of these candidates?")
        return "\n".join(lines)

    def _get_no_candidates_message(self) -> str:
        """Generates a helpful message when no candidates are found."""
        return (
            "I wasn't able to find candidates that closely match your requirements.\n\n"
            "Suggestions:\n"
            "- Try broader search terms (e.g., 'developer' instead of 'senior full-stack developer').\n"
            "- Look for related skills (e.g., 'JavaScript' instead of 'React').\n"
            "- Adjust experience requirements."
        )

    def _summary_cache_key(self, query: str, candidates: list[dict]) -> str:
        # Use stable subset of candidate fields for key stability
        ids = [str(c.get('id', c.get('name', ''))) for c in candidates[:5]]
        key = f"q:{query.strip().lower()}|ids:{','.join(ids)}"
        # Keep keys reasonably short
        return key[:512]