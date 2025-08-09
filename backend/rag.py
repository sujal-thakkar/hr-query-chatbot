# backend/rag.py
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import json
import logging
from dataclasses import dataclass
from query_processor import QueryProcessor, ProcessedQuery

@dataclass
class SearchResult:
    employee: Dict[str, Any]
    relevance_score: float
    match_reasons: List[str]
    confidence: float

class EmployeeRAG:
    def __init__(self, employees_data: List[Dict[str, Any]]):
        self.employees = employees_data
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
        self.employee_embeddings = None
        self.employee_texts = None
        self.query_processor = QueryProcessor()
        self.logger = logging.getLogger(__name__)
        self._prepare_embeddings()
        
        # Query cache for performance
        self._query_cache = {}
        self._cache_size_limit = 100
    
    def _prepare_embeddings(self):
        """Create embeddings for all employees with enhanced text representation"""
        self.employee_texts = []
        for emp in self.employees:
            # Create comprehensive text representation with weighted importance
            text_parts = [
                f"Name: {emp['name']}",
                f"Skills: {', '.join(emp['skills'])}",  # Most important
                f"Experience: {emp['experience_years']} years",
                f"Projects: {', '.join(emp['projects'])}",  # Second most important
                f"Availability: {emp['availability']}"
            ]
            
            # Add skill-project correlation context
            skill_context = self._generate_skill_context(emp)
            if skill_context:
                text_parts.append(f"Expertise areas: {skill_context}")
            
            text = " | ".join(text_parts)
            self.employee_texts.append(text)
        
        # Generate embeddings
        self.employee_embeddings = self.model.encode(self.employee_texts)
        self.logger.info(f"Generated embeddings for {len(self.employees)} employees")
    
    def _generate_skill_context(self, employee: Dict[str, Any]) -> str:
        """Generate additional context based on skill-project combinations"""
        skills = [s.lower() for s in employee['skills']]
        projects = [p.lower() for p in employee['projects']]
        
        contexts = []
        
        # ML + Healthcare context
        if any(s in skills for s in ['ml', 'tensorflow', 'pytorch', 'scikit-learn']) and \
           any('health' in p or 'medical' in p or 'patient' in p for p in projects):
            contexts.append("healthcare AI specialist")
        
        # Full-stack web development
        if any(s in skills for s in ['python', 'javascript', 'react']) and \
           any(s in skills for s in ['django', 'flask', 'nodejs']):
            contexts.append("full-stack web developer")
        
        # Mobile development
        if any(s in skills for s in ['ios', 'android', 'react native', 'flutter']):
            contexts.append("mobile app developer")
        
        # Data engineering
        if any(s in skills for s in ['python', 'sql', 'pandas']) and \
           any('data' in p or 'analytics' in p for p in projects):
            contexts.append("data engineer")
        
        # DevOps/Cloud
        if any(s in skills for s in ['aws', 'docker', 'kubernetes']):
            contexts.append("cloud infrastructure specialist")
        
        return ", ".join(contexts)
    
    def enhanced_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Enhanced search with query processing and detailed results"""
        # Check cache first
        cache_key = f"{query.lower().strip()}_{top_k}"
        if cache_key in self._query_cache:
            self.logger.info(f"Cache hit for query: {query}")
            return self._query_cache[cache_key]
        
        # Process the query
        processed_query = self.query_processor.process_query(query)
        self.logger.info(f"Processed query - Skills: {processed_query.skill_terms}, "
                        f"Domains: {processed_query.domain_context}, "
                        f"Experience: {processed_query.experience_requirements}")
        
        # Perform semantic search
        semantic_results = self._semantic_search_enhanced(processed_query, top_k * 2)
        
        # Apply advanced filtering and scoring
        filtered_results = self._apply_advanced_filtering(semantic_results, processed_query)
        
        # Generate detailed search results
        detailed_results = []
        for emp_data in filtered_results[:top_k]:
            match_reasons = self._generate_match_reasons(emp_data, processed_query)
            confidence = self._calculate_confidence(emp_data, processed_query)
            
            result = SearchResult(
                employee=emp_data,
                relevance_score=emp_data.get('final_score', 0),
                match_reasons=match_reasons,
                confidence=confidence
            )
            detailed_results.append(result)
        
        # Cache the results
        if len(self._query_cache) >= self._cache_size_limit:
            # Remove oldest entry
            oldest_key = next(iter(self._query_cache))
            del self._query_cache[oldest_key]
        self._query_cache[cache_key] = detailed_results
        
        return detailed_results
    
    def _semantic_search_enhanced(self, processed_query: ProcessedQuery, top_k: int) -> List[Dict[str, Any]]:
        """Enhanced semantic search with query processing"""
        # Use both original and cleaned query for embedding
        search_texts = [processed_query.original, processed_query.cleaned]
        if processed_query.skill_terms:
            search_texts.append(" ".join(processed_query.skill_terms))
        if processed_query.domain_context:
            search_texts.append(" ".join(processed_query.domain_context))
        
        # Average embeddings for multi-faceted queries
        query_embeddings = self.model.encode(search_texts)
        avg_query_embedding = np.mean(query_embeddings, axis=0).reshape(1, -1)
        
        # Calculate similarities
        similarities = np.dot(avg_query_embedding, self.employee_embeddings.T).flatten()
        
        # Get top candidates
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            emp = self.employees[idx].copy()
            emp['similarity_score'] = float(similarities[idx])
            results.append(emp)
        
        return results
    
    def _apply_advanced_filtering(self, candidates: List[Dict[str, Any]], 
                                processed_query: ProcessedQuery) -> List[Dict[str, Any]]:
        """Apply advanced filtering and scoring based on processed query"""
        for emp in candidates:
            total_score = emp['similarity_score']
            
            # Experience requirement filtering
            exp_req = processed_query.experience_requirements
            if 'min_years' in exp_req:
                if emp['experience_years'] >= exp_req['min_years']:
                    total_score += 0.3
                else:
                    total_score -= 0.5  # Penalty for not meeting requirements
            
            if 'max_years' in exp_req:
                if emp['experience_years'] <= exp_req['max_years']:
                    total_score += 0.2
                else:
                    total_score -= 0.2
            
            # Skill matching bonus
            emp_skills_lower = [s.lower() for s in emp['skills']]
            skill_matches = 0
            for skill in processed_query.skill_terms:
                if any(skill.lower() in emp_skill for emp_skill in emp_skills_lower):
                    skill_matches += 1
                    total_score += 0.4
            
            # Domain context bonus
            emp_projects_text = " ".join(emp['projects']).lower()
            for domain in processed_query.domain_context:
                domain_keywords = self.query_processor.domain_keywords.get(domain, [])
                if any(keyword in emp_projects_text for keyword in domain_keywords):
                    total_score += 0.3
            
            # Availability preference
            if emp['availability'] == 'available':
                total_score += 0.1
            elif emp['availability'] == 'busy':
                total_score -= 0.2
            
            emp['final_score'] = total_score
            emp['skill_match_count'] = skill_matches
        
        # Sort by final score
        candidates.sort(key=lambda x: x['final_score'], reverse=True)
        return candidates
    
    def _generate_match_reasons(self, employee: Dict[str, Any], 
                              processed_query: ProcessedQuery) -> List[str]:
        """Generate human-readable match reasons"""
        reasons = []
        
        # Skill matches
        emp_skills_lower = [s.lower() for s in employee['skills']]
        for skill in processed_query.skill_terms:
            if any(skill.lower() in emp_skill for emp_skill in emp_skills_lower):
                matching_skill = next(s for s in employee['skills'] if skill.lower() in s.lower())
                reasons.append(f"Has required skill: {matching_skill}")
        
        # Experience match
        exp_req = processed_query.experience_requirements
        if 'min_years' in exp_req:
            if employee['experience_years'] >= exp_req['min_years']:
                reasons.append(f"Meets experience requirement: {employee['experience_years']} years")
        
        # Domain experience
        emp_projects_text = " ".join(employee['projects']).lower()
        for domain in processed_query.domain_context:
            domain_keywords = self.query_processor.domain_keywords.get(domain, [])
            if any(keyword in emp_projects_text for keyword in domain_keywords):
                reasons.append(f"Has {domain} domain experience")
        
        # Availability
        if employee['availability'] == 'available':
            reasons.append("Currently available")
        
        return reasons
    
    def _calculate_confidence(self, employee: Dict[str, Any], 
                            processed_query: ProcessedQuery) -> float:
        """Calculate confidence score for the match"""
        confidence = 0.0
        
        # Base confidence from similarity
        confidence += min(employee.get('similarity_score', 0) * 100, 40)
        
        # Skill match confidence
        skill_match_ratio = employee.get('skill_match_count', 0) / max(len(processed_query.skill_terms), 1)
        confidence += skill_match_ratio * 30
        
        # Experience confidence
        exp_req = processed_query.experience_requirements
        if 'min_years' in exp_req:
            if employee['experience_years'] >= exp_req['min_years']:
                confidence += 20
        else:
            confidence += 10  # Bonus for no specific requirement
        
        # Domain experience confidence
        if processed_query.domain_context:
            emp_projects_text = " ".join(employee['projects']).lower()
            domain_matches = sum(1 for domain in processed_query.domain_context
                               if any(keyword in emp_projects_text 
                                    for keyword in self.query_processor.domain_keywords.get(domain, [])))
            confidence += (domain_matches / len(processed_query.domain_context)) * 10
        
        return min(confidence, 100.0)
    
    # Keep existing hybrid_search for backward compatibility
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Backward compatible hybrid search - delegates to enhanced search"""
        results = self.enhanced_search(query, top_k)
        # Convert SearchResult objects back to dictionaries for compatibility
        return [result.employee for result in results]
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Backward compatible semantic search"""
        # Simple semantic search without query processing
        query_embedding = self.model.encode([query])
        similarities = np.dot(query_embedding, self.employee_embeddings.T).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            emp = self.employees[idx].copy()
            emp['similarity_score'] = float(similarities[idx])
            results.append(emp)
        
        return results

# Usage example:
# rag = EmployeeRAG(employees_data)
# results = rag.hybrid_search("Python developer with healthcare experience", top_k=5)
