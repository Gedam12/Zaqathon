import csv
import json
import re
from datetime import datetime

class OrderProcessor:
    def __init__(self):
        self.catalog = {}
    
    def load_catalog(self, csv_file):
        """Load catalog from CSV - handles different header names"""
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            # Print headers for debugging
            print("CSV Headers:", reader.fieldnames)
            
            for row in reader:
                # Try different possible SKU column names
                sku = None
                for key in row.keys():
                    if key.lower() in ['sku', 'product_id', 'productid', 'product id', 'item', 'code']:
                        sku = row[key].strip()
                        break
                
                if not sku:
                    print("Warning: Could not find SKU column. Using first column.")
                    sku = list(row.values())[0].strip()
                
                # Handle different column names
                description = ""
                moq = 1
                price = 0
                stock = 0
                
                for key, value in row.items():
                    key_lower = key.lower()
                    if 'description' in key_lower or 'name' in key_lower:
                        description = value.strip()
                    elif 'moq' in key_lower or 'minimum' in key_lower:
                        moq = int(value) if value.isdigit() else 1
                    elif 'price' in key_lower or 'cost' in key_lower:
                        price = float(value) if value.replace('.','').isdigit() else 0
                    elif 'stock' in key_lower or 'inventory' in key_lower or 'qty' in key_lower:
                        stock = int(value) if value.isdigit() else 0
                
                self.catalog[sku] = {
                    'sku': sku,
                    'description': description,
                    'moq': moq,
                    'price': price,
                    'stock': stock
                }
    
    # ... rest of the code stays the same ...
    def extract_orders(self, email_text):
        orders = []
        sku_patterns = [
            r'\b([A-Z]{2,}[-_]?[0-9]{2,})\b',
            r'\b([A-Z0-9]{3,}[-_][A-Z0-9]{2,})\b',
            r'SKU[:\s]*([A-Z0-9-_]+)',
            r'Product[:\s]*([A-Z0-9-_]+)'
        ]
        
        urgent_keywords = ['urgent', 'asap', 'rush', 'immediately', 'priority']
        delivery = 'standard'
        for keyword in urgent_keywords:
            if keyword.lower() in email_text.lower():
                delivery = 'urgent'
                break
        
        lines = email_text.split('\n')
        for line in lines:
            for pattern in sku_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    sku = match.group(1).upper()
                    qty_match = re.search(r'(\d+)[\s\w]*(?:pcs?|pieces?|units?|qty|quantity)?', line, re.IGNORECASE)
                    quantity = int(qty_match.group(1)) if qty_match else 1
                    
                    orders.append({
                        'sku': sku,
                        'quantity': quantity,
                        'notes': line.strip(),
                        'delivery': delivery
                    })
        return orders
    
    def validate_orders(self, orders):
        validated = []
        suggestions = []
        
        for order in orders:
            result = {**order, 'status': 'valid', 'issues': []}
            
            if order['sku'] not in self.catalog:
                result['status'] = 'invalid'
                result['issues'].append('SKU not found')
                similar = self.find_similar_skus(order['sku'])
                if similar:
                    suggestions.append(f"{order['sku']} not found. Try: {', '.join(similar)}")
            else:
                item = self.catalog[order['sku']]
                if order['quantity'] < item['moq']:
                    result['status'] = 'warning'
                    result['issues'].append(f"Below MOQ ({item['moq']})")
                    suggestions.append(f"Increase {order['sku']} to {item['moq']} units")
                if order['quantity'] > item['stock']:
                    result['status'] = 'warning' 
                    result['issues'].append(f"Low stock ({item['stock']} available)")
                    suggestions.append(f"Reduce {order['sku']} to {item['stock']} or backorder")
            
            validated.append(result)
        
        return {'orders': validated, 'suggestions': suggestions, 'timestamp': datetime.now().isoformat()}
    
    def find_similar_skus(self, target):
        similar = []
        for sku in self.catalog.keys():
            if target[:3] in sku or sku[:3] in target:
                similar.append(sku)
        return similar[:3]

def main():
    processor = OrderProcessor()
    catalog_file = input("Catalog CSV file: ").strip()
    processor.load_catalog(catalog_file)
    print(f"✅ Loaded {len(processor.catalog)} products")
    
    email_file = input("Email TXT file: ").strip()
    with open(email_file, 'r') as f:
        email_text = f.read()
    
    orders = processor.extract_orders(email_text)
    result = processor.validate_orders(orders)
    
    print(f"\n📦 EXTRACTED {len(result['orders'])} ORDERS:")
    for order in result['orders']:
        status_color = "✅" if order['status'] == 'valid' else "⚠️" if order['status'] == 'warning' else "❌"
        print(f"{status_color} {order['sku']} x{order['quantity']} - {order['status']}")
        if order['issues']:
            print(f"   Issues: {', '.join(order['issues'])}")
    
    print(f"\n💡 SUGGESTIONS:")
    for suggestion in result['suggestions']:
        print(f"• {suggestion}")
    
    with open('order_output.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Saved to: order_output.json")

if __name__ == "__main__":
    main()

    class OrderProcessor:
    def __init__(self):
        self.catalog = {}
    
    # ... existing methods ...
    
    def add_confidence_scores(self, orders):
        """ADD THIS METHOD"""
        for order in orders:
            confidence = 1.0
            if order['sku'] not in self.catalog:
                confidence = 0.0
            elif len(order['sku']) < 4:
                confidence = 0.5
            elif order['status'] == 'warning':
                confidence = 0.7
            order['confidence'] = confidence
        return orders
    
    def validate_orders(self, orders):
        # ... existing code ...
        result = {
            'orders': validated,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
        
        # ADD THIS LINE BEFORE RETURN
        result['orders'] = self.add_confidence_scores(result['orders'])
        return result