import pandas as pd
from typing import Dict, List
from difflib import get_close_matches

class CatalogValidator:
    def __init__(self, catalog_path: str):
        self.catalog = pd.read_csv(catalog_path)
        self.catalog['SKU'] = self.catalog['SKU'].str.upper()
    
    def validate_order(self, items: List[Dict]) -> Dict:
        """Validate all items and return comprehensive results"""
        results = {
            "valid_items": [],
            "issues": [],
            "suggestions": [],
            "total_value": 0
        }
        
        for item in items:
            sku = item["sku"].upper()
            qty = item["quantity"]
            
            # Find in catalog
            cat_item = self.catalog[self.catalog['SKU'] == sku]
            
            if cat_item.empty:
                # SKU not found
                suggestions = get_close_matches(sku, self.catalog['SKU'].tolist(), n=2, cutoff=0.6)
                results["issues"].append({
                    "type": "invalid_sku",
                    "sku": sku,
                    "message": f"SKU {sku} not found",
                    "suggestions": suggestions
                })
                continue
            
            row = cat_item.iloc[0]
            moq = row.get('MOQ', 1)
            stock = row.get('Stock', 999)
            price = row.get('Price', 0)
            
            # Validate MOQ
            if qty < moq:
                results["issues"].append({
                    "type": "moq_violation",
                    "sku": sku,
                    "requested": qty,
                    "minimum": moq,
                    "message": f"{sku}: Need {moq} minimum, got {qty}"
                })
            
            # Validate stock
            if qty > stock:
                results["issues"].append({
                    "type": "stock_shortage",
                    "sku": sku,
                    "requested": qty,
                    "available": stock,
                    "message": f"{sku}: Only {stock} available, need {qty}"
                })
            
            # Add to valid items
            results["valid_items"].append({
                "sku": sku,
                "description": row.get('Description', 'N/A'),
                "quantity": qty,
                "unit_price": price,
                "total_price": qty * price,
                "moq_ok": qty >= moq,
                "stock_ok": qty <= stock
            })
            
            results["total_value"] += qty * price
        
        # Generate smart suggestions
        results["suggestions"] = self._generate_suggestions(results["issues"])
        
        return results
    
    def _generate_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generate actionable suggestions"""
        suggestions = []
        
        for issue in issues:
            if issue["type"] == "invalid_sku" and issue["suggestions"]:
                suggestions.append(f"Replace {issue['sku']} with {issue['suggestions'][0]}?")
            
            elif issue["type"] == "moq_violation":
                need = issue["minimum"] - issue["requested"]
                suggestions.append(f"Add {need} more {issue['sku']} to meet MOQ")
            
            elif issue["type"] == "stock_shortage":
                available = issue["available"]
                suggestions.append(f"Reduce {issue['sku']} to {available} units or split order")
        
        return suggestions
    
    def get_sku_info(self, sku: str) -> Dict:
        """Get detailed SKU information"""
        item = self.catalog[self.catalog['SKU'] == sku.upper()]
        if item.empty:
            return {"found": False}
        
        row = item.iloc[0]
        return {
            "found": True,
            "sku": row['SKU'],
            "description": row.get('Description', ''),
            "price": row.get('Price', 0),
            "moq": row.get('MOQ', 1),
            "stock": row.get('Stock', 0)
        }
