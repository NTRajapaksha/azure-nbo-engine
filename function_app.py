import azure.functions as func
import logging
import pandas as pd
from azure.storage.blob import BlobClient
from io import StringIO
import os
import json  # <--- NEW IMPORT

# --- CONFIGURATION ---
CONN_STR = os.environ["NBO_STORAGE_CONN"]
CONTAINER = "nbo-data"
BLOB_NAME = "nbo_predictions.csv"

app = func.FunctionApp()

@app.route(route="recommend", auth_level=func.AuthLevel.ANONYMOUS)
def recommend(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('NBO Request Received.')

    customer_id = req.params.get('id')
    if not customer_id:
        return func.HttpResponse("Please pass a customer 'id'", status_code=400)

    try:
        # 1. Connect
        blob = BlobClient.from_connection_string(conn_str=CONN_STR, container_name=CONTAINER, blob_name=BLOB_NAME)
        
        # 2. Download
        download_stream = blob.download_blob()
        csv_data = download_stream.readall().decode('utf-8')
        
        # 3. Load
        df = pd.read_csv(StringIO(csv_data))
        
        # 4. Filter
        recs = df[df['customer_id'] == int(customer_id)]
        
        if recs.empty:
             return func.HttpResponse(f"No recommendations found for Customer {customer_id}", status_code=404)

        result = recs[['product_id', 'name', 'category', 'prediction_score']].to_dict(orient='records')

        # --- THE FIX IS HERE ---
        # We use json.dumps() to ensure strictly valid JSON (Double Quotes)
        return func.HttpResponse(
            body=json.dumps(result), 
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)