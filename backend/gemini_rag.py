import numpy as np
from typing import List, Dict, Any, Optional
import json
import logging
from query_processor import QueryProcessor, ProcessedQuery
from ai_client import GeminiClient
from shared_models import SearchResult, DEFAULT_EMBEDDING_DIMENSION, DEFAULT_CACHE_SIZE_LIMIT

class GeminiEmployeeRAG:
    """Enhanced Employee RAG using Gemini's native embeddings with proper task types"""
    
    def __init__(self, employees_data: List[Dict[str, Any]], api_key: Optional[str] = None):
        self.employees = employees_data
        self.gemini_client = GeminiClient(api_key)
        self.employee_embeddings = None
        self.employee_texts = None
        self.query_processor = QueryProcessor()
        self.logger = logging.getLogger(__name__)
        
        # Embedding configuration using shared constants
        self.embedding_dimension = DEFAULT_EMBEDDING_DIMENSION
        
        # Query cache for performance using shared constants
        self._query_cache = {}
        self._cache_size_limit = DEFAULT_CACHE_SIZE_LIMIT
        
        if self.gemini_client.is_available():
            self._prepare_embeddings()
        else:
            raise Exception("Gemini client not available for embeddings")
    
    def _prepare_embeddings(self):
        """Create embeddings for all employees using Gemini's embedding model"""
        self.employee_texts = []
        
        for emp in self.employees:
            # Create comprehensive text representation optimized for document retrieval
            text_parts = [
                f"Employee: {emp['name']}",
                f"Technical Skills: {', '.join(emp['skills'])}",
                f"Professional Experience: {emp['experience_years']} years in the industry",
                f"Project Portfolio: {', '.join(emp['projects'])}",
                f"Current Status: {emp['availability']}"
            ]
            
            # Add skill-project correlation context
            skill_context = self._generate_skill_context(emp)
            if skill_context:
                text_parts.append(f"Specialization Areas: {skill_context}")
            
            # Add domain expertise context
            domain_context = self._generate_domain_context(emp)
            if domain_context:
                text_parts.append(f"Domain Expertise: {domain_context}")
            
            text = " | ".join(text_parts)
            self.employee_texts.append(text)
        
        # Generate embeddings using Gemini with RETRIEVAL_DOCUMENT task type
        try:
            self.logger.info("Generating embeddings using Gemini embedding model...")
            embeddings_list = self.gemini_client.get_batch_embeddings(
                texts=self.employee_texts,
                task_type="RETRIEVAL_DOCUMENT",  # Optimized for document search
                output_dimensionality=self.embedding_dimension
            )
            self.employee_embeddings = np.array(embeddings_list)
            self.logger.info(f"✅ Generated Gemini embeddings for {len(self.employees)} employees")
        except Exception as e:
            self.logger.error(f"❌ Failed to generate embeddings: {e}")
            raise
    
    def _generate_skill_context(self, employee: Dict[str, Any]) -> str:
        """Generate additional context based on skill combinations"""
        skills = [s.lower() for s in employee['skills']]
        projects = [p.lower() for p in employee['projects']]
        
        contexts = []
        
        # AI/ML specialist
        if any(s in skills for s in ['tensorflow', 'pytorch', 'scikit-learn', 'machine learning', 'ai']):
            contexts.append("artificial intelligence and machine learning specialist")
        
        # Full-stack developer
        if any(s in skills for s in ['python', 'javascript', 'react']) and \
           any(s in skills for s in ['django', 'flask', 'nodejs', 'express']):
            contexts.append("full-stack web application developer")
        
        # Mobile developer
        if any(s in skills for s in ['ios', 'android', 'react native', 'flutter', 'swift', 'kotlin']):
            contexts.append("mobile application developer")
        
        # Data specialist
        if any(s in skills for s in ['python', 'sql', 'pandas', 'numpy']) and \
           any('data' in p or 'analytics' in p or 'visualization' in p for p in projects):
            contexts.append("data science and analytics expert")
        
        # DevOps/Cloud engineer
        if any(s in skills for s in ['aws', 'docker', 'kubernetes', 'terraform', 'devops']):
            contexts.append("cloud infrastructure and DevOps engineer")
        
        # Frontend specialist
        if any(s in skills for s in ['react', 'vue', 'angular', 'typescript', 'css']):
            contexts.append("frontend user interface specialist")
        
        # Backend specialist
        if any(s in skills for s in ['python', 'java', 'nodejs', 'go', 'rust']) and \
           any(s in skills for s in ['api', 'microservices', 'database']):
            contexts.append("backend systems and API developer")
        
        return ", ".join(contexts)
    
    def _generate_domain_context(self, employee: Dict[str, Any]) -> str:
        """Generate domain-specific context from projects"""
        projects_text = " ".join(employee['projects']).lower()
        domains = []
        
        # Healthcare/Medical
        if any(keyword in projects_text for keyword in ['health', 'medical', 'patient', 'hospital', 'clinic']):
            domains.append("healthcare and medical systems")
        
        # E-commerce/Retail
        if any(keyword in projects_text for keyword in ['shop', 'commerce', 'retail', 'payment', 'checkout']):
            domains.append("e-commerce and retail solutions")
        
        # Finance/Fintech
        if any(keyword in projects_text for keyword in ['banking', 'finance', 'payment', 'trading', 'crypto']):
            domains.append("financial technology and services")
        
        # Education/EdTech
        if any(keyword in projects_text for keyword in ['education', 'learning', 'course', 'student', 'school']):
            domains.append("educational technology")
        
        # Gaming
        if any(keyword in projects_text for keyword in ['game', 'gaming', 'unity', 'unreal']):
            domains.append("game development")
        
        # Social Media/Communication
        if any(keyword in projects_text for keyword in ['social', 'chat', 'messaging', 'communication']):
            domains.append("social media and communication platforms")
        
        return ", ".join(domains)
    
    def enhanced_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Enhanced search with Gemini embeddings and query processing"""
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
        
        # Perform semantic search using Gemini embeddings
        semantic_results = self._semantic_search_with_gemini(processed_query, top_k * 2)
        
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
            oldest_key = next(iter(self._query_cache))
            del self._query_cache[oldest_key]
        self._query_cache[cache_key] = detailed_results
        
        return detailed_results
    
    def _semantic_search_with_gemini(self, processed_query: ProcessedQuery, top_k: int) -> List[Dict[str, Any]]:
        """Semantic search using Gemini embeddings with proper task types"""
        # Create optimized search query
        search_components = [processed_query.cleaned]
        
        if processed_query.skill_terms:
            search_components.append(f"Required skills: {', '.join(processed_query.skill_terms)}")
        
        if processed_query.domain_context:
            search_components.append(f"Domain experience: {', '.join(processed_query.domain_context)}")
        
        if processed_query.experience_requirements:
            exp_req = processed_query.experience_requirements
            if 'min_years' in exp_req:
                search_components.append(f"Minimum {exp_req['min_years']} years experience")
        
        # Combine components for a comprehensive search query
        search_query = " | ".join(search_components)
        
        try:
            # Generate query embedding with RETRIEVAL_QUERY task type
            query_embedding = self.gemini_client.get_embedding(
                text=search_query,
                task_type="RETRIEVAL_QUERY",  # Optimized for search queries
                output_dimensionality=self.embedding_dimension
            )
            query_embedding = np.array(query_embedding).reshape(1, -1)
            
            # Calculate cosine similarities
            similarities = np.dot(query_embedding, self.employee_embeddings.T).flatten()
            
            # Get top candidates
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                emp = self.employees[idx].copy()
                emp['similarity_score'] = float(similarities[idx])
                results.append(emp)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in Gemini semantic search: {e}")
            raise
    
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
        
        # Base confidence from similarity (Gemini embeddings are typically higher quality)
        confidence += min(employee.get('similarity_score', 0) * 100, 45)
        
        # Skill match confidence
        skill_match_ratio = employee.get('skill_match_count', 0) / max(len(processed_query.skill_terms), 1)
        confidence += skill_match_ratio * 30
        
        # Experience confidence
        exp_req = processed_query.experience_requirements
        if 'min_years' in exp_req:
            if employee['experience_years'] >= exp_req['min_years']:
                confidence += 20
        else:
            confidence += 10
        
        # Domain experience confidence
        if processed_query.domain_context:
            emp_projects_text = " ".join(employee['projects']).lower()
            domain_matches = sum(1 for domain in processed_query.domain_context
                               if any(keyword in emp_projects_text 
                                    for keyword in self.query_processor.domain_keywords.get(domain, [])))
            confidence += (domain_matches / len(processed_query.domain_context)) * 5
        
        return min(confidence, 100.0)
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Simple semantic search using Gemini embeddings"""
        try:
            query_embedding = self.gemini_client.get_embedding(
                text=query,
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=self.embedding_dimension
            )
            query_embedding = np.array(query_embedding).reshape(1, -1)
            
            similarities = np.dot(query_embedding, self.employee_embeddings.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                emp = self.employees[idx].copy()
                emp['similarity_score'] = float(similarities[idx])
                results.append(emp)
            
            return results
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            raise

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding setup"""
        if self.employee_embeddings is not None:
            return {
                "embedding_model": "gemini-embedding-001",
                "dimension": self.embedding_dimension,
                "total_employees": len(self.employees),
                "embedding_shape": self.employee_embeddings.shape,
                "task_type": "RETRIEVAL_DOCUMENT",
                "normalization": "Applied for dimensions < 3072"
            }
        return {"status": "Embeddings not initialized"}
