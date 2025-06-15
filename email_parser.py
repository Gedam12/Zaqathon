import re
import json
import openai
from typing import Dict, List

class EmailParser:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        
    def parse(self, email_text: str) -> Dict:
        """Parse email and return order data"""
        try:
            return self._llm_parse(email_text)
        except:
            return self._regex_parse(email_text)
    
    def _llm_parse(self, text: str) -> Dict:
        """LLM extraction"""
        prompt = f"""Extract order info. Return JSON only:
        {{
            "customer": {{"name": "", "email": ""}},
            "items": [{{"sku": "", "quantity": 1}}],
            "delivery": "address",
            "notes": "",
            "confidence": 0.8
        }}
        
        Email: {text[:1200]}"""
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _regex_parse(self, text: str) -> Dict:
        """Regex fallback"""
        # Extract SKUs and quantities
        skus = re.findall(r'\b[A-Z]{2,4}[-_]?\d{3,6}\b', text, re.IGNORECASE)
        qtys = re.findall(r'(?:qty|quantity)\s*:?\s*(\d+)', text, re.IGNORECASE)
        
        # Build items
        items = []
        for i, sku in enumerate(skus):
            qty = int(qtys[i]) if i < len(qtys) else 1
            items.append({"sku": sku.upper(), "quantity": qty})
        
        # Extract customer info
        email = re.findall(r'\b[\w.-]+@[\w.-]+\.\w+\b', text)
        name_match = re.search(r'(?:From:|Best,|Regards,)\s*([A-Za-z\s]+)', text)
        
        return {
            "customer": {
                "name": name_match.group(1).strip() if name_match else "Unknown",
                "email": email[0] if email else ""
            },
            "items": items,
            "delivery": self._extract_address(text),
            "notes": "Regex extraction",
            "confidence": 0.6
        }
    
    def _extract_address(self, text: str) -> str:
    """Extract delivery address"""
    patterns = [
        r'(?:ship to|deliver to|address):\s*([^\n]+)',
        r'(\d+\s+[A-Za-z\s]+(?:St|Ave|Rd|Blvd|Street))',
        r'([A-Za-z\s]+,\s*[A-Za-z\s]+,?\s*\d{5})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Address TBD"
