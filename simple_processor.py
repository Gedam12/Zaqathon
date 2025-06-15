# Create simple_processor.py
import json

def process_email():
    order = {
        "order_id": "ORD-123",
        "customer": {"name": "John Smith"},
        "items": [{"sku": "STRÅDAL620", "quantity": 9}],
        "status": "validated"
    }
    
    with open("order.json", "w") as f:
        json.dump(order, f, indent=2)
    
    print("Order saved to order.json")

if __name__ == "__main__":
    process_email()