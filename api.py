# Import standart libraries
import os
from flask import Flask, jsonify, request
from google.cloud import vision
from firebase_admin import firestore

# Initialize Flask Application
app = Flask(__name__)

# API that returns JSON as a result after processing an image
@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    # Creates AutoVision client
    visionClient = vision.ImageAnnotatorClient()

    # Receive the uri and file name from url
    uri = request.values.get("uri")
    fileName = request.values.get("fileName")

    # Analyze the image from bucket with AutoVision
    result = visionClient.label_detection(image=vision.Image(source=vision.ImageSource(image_uri=uri+fileName)))
    labels = []
    for label in result.label_annotations:
        labels.append(label.description)

    # Check whether the image containing a 'food' label
    filters = ["Food", "Recipe", "Ingredient"]
    for filter in filters:
        if filter in labels:
            return jsonify({
                "status": 200,
                "message": {
                    "imagePath": fileName,
                    "information": labels
                }
            }), 200
        else:
            return jsonify({
                "status": 200,
                "message": {
                    "imagePath": fileName,
                    "information": ["This is not an image containing either Food, Recipe, or Ingredient"]
                }
            }), 200

# API that returns a list of the image along with information about the image from Firestore
@app.route("/databasequery", methods=["GET"])
def databaseQuery():
    # Creates a Firestore client
    firestoreClient = firestore.Client()
    # Create a reference to the 'images' collection
    collectionRef = firestoreClient.collection(u"images")

    # Query all the document listed in the 'images' collection
    queryResult = []
    for doc in collectionRef.stream():
        docContent = []
        for field, info in doc.to_dict().items():
            docContent.append({field: info})

        queryResult.append(
            {
                "docId": doc.id,
                "docContent": docContent
            }
        )

    return jsonify({
        "status": 200,
        "message": queryResult
    })

# API that returns a specific image along with information about the image from Firestore
@app.route("/query", methods=["GET"])
def query():
    # Recieve the image file name from url
    image = request.values.get("image")
    # Creates a Firestore client
    firestoreClient = firestore.Client()
    # Create a reference to the 'images' collection and find specific image
    documentRef = firestoreClient.collection(u"images").document(image)
    # Get the image data
    doc = documentRef.get()
    if doc.exists:
        return jsonify({
            "status": 200,
            "message": doc.to_dict()
        }), 200

port = int(os.environ.get("PORT", 8080))
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=port)
