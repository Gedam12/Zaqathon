from flask import Flask, request, render_template_string, jsonify
from order_processor import OrderProcessor  # Import your class
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        catalog_file = request.files['catalog']
        email_file = request.files['email']
        
        # Save temporarily and process
        catalog_file.save('temp_catalog.csv')
        email_file.save('temp_email.txt')
        
        processor = OrderProcessor()
        processor.load_catalog('temp_catalog.csv')
        
        with open('temp_email.txt', 'r') as f:
            email_text = f.read()
        
        orders = processor.extract_orders(email_text)
        result = processor.validate_orders(orders)
        
        return jsonify(result)
    
    return '''
    <html><body>
    <h1>Smart Order Intake</h1>
    <form method=post enctype=multipart/form-data>
      Catalog CSV: <input type=file name=catalog accept=".csv"><br><br>
      Email TXT: <input type=file name=email accept=".txt"><br><br>
      <input type=submit value="Process Order">
    </form>
    </body></html>
    '''

if __name__ == '__main__':
    app.run(debug=True)