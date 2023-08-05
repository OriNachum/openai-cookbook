from flask import Flask, request, jsonify
from flasgger import Swagger
from embedding_service import EmbeddingService
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)
swagger = Swagger(app)

embedding_service = EmbeddingService("TipGPT_Question")

@app.route("/insert", methods=["POST"])
def insert_records():
    """
    Insert records into Milvus
    ---
    parameters:
      - name: records
        in: body
        required: true
        type: array
        items:
            type: object
            properties:
                owner:
                    type: string
                question:
                    type: string
                answer:
                    type: string
    responses:
        200:
            description: Records inserted successfully
    """
    records = request.json["records"]
    embedding_service.insert_records(records)
    return jsonify({"message": "Records inserted successfully"}), 200

@app.route("/search", methods=["POST"])
def search_records():
    """
    Search records in Milvus
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
            properties:
                query:
                    type: string
                top_k:
                    type: integer
    responses:
        200:
            description: Search Results
    """
    query = request.json.get("query")
    top_k = request.json.get("top_k", 10)
    results = embedding_service.search_records(query, top_k)

    return jsonify({"results": results}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
