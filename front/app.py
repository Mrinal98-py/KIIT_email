from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Create a connection to the MongoDB server
client = MongoClient("mongodb+srv://Mrinal:getdataold@mrinal.8kbejgd.mongodb.net/?retryWrites=true&w=majority")

# Access the database and collection
db = client['email_database']
collection = db['email_collection']

def split_date(date_str):
    return date_str.split('+')[0]

# Register the custom filter
app.jinja_env.filters['split_date'] = split_date


@app.route('/', methods=['GET'])
def get_email_data():
    # Retrieve all records from the MongoDB collection
    records = list(collection.find())

    if records:
        # Pass the records to the HTML template
        return render_template('email_data.html', records=records)
    else:
        return "No data found in the collection"
    
if __name__ == '__main__':
    app.run()  # Change the port to 5001
