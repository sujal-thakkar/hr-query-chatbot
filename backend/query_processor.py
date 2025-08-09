# backend/query_processor.py
import re
from typing import List, Dict, Tuple
from shared_models import ProcessedQuery, SKILL_SYNONYMS, DOMAIN_KEYWORDS

class QueryProcessor:
    """Advanced query preprocessing for better RAG performance"""
    
    def __init__(self):
        # Use shared mappings from shared_models
        self.skill_synonyms = SKILL_SYNONYMS
        self.domain_keywords = DOMAIN_KEYWORDS
        
        self.experience_patterns = [
            (r'(\d+)\s*\+?\s*(?:years?|yrs?)', 'min_years'),
            (r'(?:minimum|min|at least)\s*(\d+)\s*(?:years?|yrs?)', 'min_years'),
            (r'(\d+)-(\d+)\s*(?:years?|yrs?)', 'range_years'),
            (r'(?:senior|sr\.?)', 'senior_level'),
            (r'(?:junior|jr\.?|entry)', 'junior_level'),
            (r'(?:mid|middle)', 'mid_level'),
            (r'(?:lead|principal|architect)', 'lead_level')
        ]
    
    def process_query(self, query: str) -> ProcessedQuery:
        """Main query processing pipeline"""
        original = query
        cleaned = self._clean_query(query)
        keywords = self._extract_keywords(cleaned)
        skill_terms = self._identify_skills(cleaned, keywords)
        experience_req = self._extract_experience_requirements(cleaned)
        domain_context = self._identify_domain_context(cleaned, keywords)
        priority_score = self._calculate_priority_score(keywords, skill_terms, domain_context)
        
        return ProcessedQuery(
            original=original,
            cleaned=cleaned,
            keywords=keywords,
            skill_terms=skill_terms,
            experience_requirements=experience_req,
            domain_context=domain_context,
            priority_score=priority_score
        )
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query"""
        # Convert to lowercase
        cleaned = query.lower().strip()
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove special characters but keep important ones
        cleaned = re.sub(r'[^\w\s\+\-\.]', ' ', cleaned)
        
        # Normalize common variations
        replacements = {
            'w/': 'with',
            'w/o': 'without',
            '&': 'and',
            '+': 'plus',
            'exp': 'experience',
            'dev': 'developer',
            'eng': 'engineer'
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned.strip()
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        # Split into words and filter stopwords
        stopwords = {
            'i', 'need', 'want', 'looking', 'for', 'someone', 'with', 'who', 'has', 'can', 'is', 'are',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'from', 'by', 'about',
            'that', 'this', 'these', 'those', 'be', 'been', 'being', 'have', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'project', 'work'
        }
        
        words = query.split()
        keywords = [word for word in words if len(word) > 2 and word not in stopwords]
        
        # Add expanded synonyms
        expanded_keywords = keywords.copy()
        for keyword in keywords:
            if keyword in self.skill_synonyms:
                expanded_keywords.extend(self.skill_synonyms[keyword])
        
        return list(set(expanded_keywords))
    
    def _identify_skills(self, query: str, keywords: List[str]) -> List[str]:
        """Identify technical skills and technologies"""
        known_skills = {
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
            'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'spring', 'laravel',
            'html', 'css', 'sass', 'scss', 'bootstrap', 'tailwind',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'opencv',
            'git', 'github', 'gitlab', 'ci/cd', 'devops', 'agile', 'scrum',
            'ios', 'android', 'react native', 'flutter', 'swift', 'kotlin',
            'machine learning', 'ai', 'data science', 'deep learning', 'nlp', 'computer vision',
            'ml', 'artificial intelligence', 'sklearn'
        }
        
        skill_terms = []
        query_lower = query.lower()
        
        # Check for exact skill matches in query
        for skill in known_skills:
            if skill in query_lower:
                skill_terms.append(skill)
        
        # Check for skills in keyword list  
        for keyword in keywords:
            if keyword in known_skills:
                skill_terms.append(keyword)
        
        # Handle synonyms and abbreviations
        for keyword in keywords:
            if keyword in self.skill_synonyms:
                skill_terms.extend(self.skill_synonyms[keyword])
        
        # Special handling for ML variations
        if any(term in query_lower for term in ['ml', 'machine learning', 'ai', 'artificial intelligence']):
            if 'machine learning' not in skill_terms:
                skill_terms.append('machine learning')
            if 'ml' not in skill_terms:
                skill_terms.append('ml')
        
        return list(set(skill_terms))
    
    def _extract_experience_requirements(self, query: str) -> Dict[str, int]:
        """Extract experience level requirements"""
        requirements = {}
        
        for pattern, req_type in self.experience_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                if req_type == 'min_years':
                    requirements['min_years'] = int(matches[0])
                elif req_type == 'range_years':
                    requirements['min_years'] = int(matches[0][0])
                    requirements['max_years'] = int(matches[0][1])
                elif req_type in ['senior_level', 'lead_level']:
                    requirements['min_years'] = 5
                elif req_type == 'mid_level':
                    requirements['min_years'] = 3
                elif req_type == 'junior_level':
                    requirements['max_years'] = 2
        
        return requirements
    
    def _identify_domain_context(self, query: str, keywords: List[str]) -> List[str]:
        """Identify business domain context"""
        domains = []
        
        for domain, domain_keywords in self.domain_keywords.items():
            if any(dk in query for dk in domain_keywords) or any(dk in keywords for dk in domain_keywords):
                domains.append(domain)
        
        return domains
    
    def _calculate_priority_score(self, keywords: List[str], skills: List[str], domains: List[str]) -> float:
        """Calculate query complexity/priority score"""
        score = 0.0
        
        # Base score from keyword count
        score += len(keywords) * 0.1
        
        # Skill specificity bonus
        score += len(skills) * 0.3
        
        # Domain context bonus
        score += len(domains) * 0.2
        
        # Complex query bonus (multiple requirements)
        if len(skills) > 2:
            score += 0.5
        if len(domains) > 1:
            score += 0.3
        
        return min(score, 5.0)  # Cap at 5.0

# Example usage and testing
if __name__ == "__main__":
    processor = QueryProcessor()
    
    test_queries = [
        "I need a senior Python developer with 5+ years experience in healthcare",
        "Looking for ML engineer with TensorFlow and medical AI experience",
        "React developer for fintech project with payment processing",
        "Junior data scientist with pandas and machine learning skills"
    ]
    
    for query in test_queries:
        result = processor.process_query(query)
        print(f"Query: {query}")
        print(f"Skills: {result.skill_terms}")
        print(f"Experience: {result.experience_requirements}")
        print(f"Domains: {result.domain_context}")
        print(f"Priority: {result.priority_score:.2f}")
        print("-" * 50)
