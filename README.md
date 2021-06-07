# flaskCloudRunAPI
 Bangkit Final Project 2021.
# Descriptions
 This source code is to analyze an image (using AutoML Vision) stored in Google Cloud Storage through an APIs service made from Flask. This service will run on a container on top of Google Cloud Run.
# Instructions
 1. Create a project in Firebase console (which synchronously integrated with Google Cloud in the background procecss) via https://console.firebase.google.com
 2. Choose Storage option and follow the provided guidance to create a Cloud Storage.
 3. Choose Firestore Database option and follow the provided guidance to create a Firestore Database.
 4. Open/provision a Cloud Shell.
     1. Set environment variable:
        ```
        export PROJECT_ID=$(gcloud info --format='value(config.project)');
        gcloud config set project $PROJECT_ID
        gcloud config set compute/region asia-southeast2
        gcloud config set compute/zone asia-southeast2-a
        ```
     2. Enable Cloud Run API, Cloud Build API, and AutoML Vision API:
        ```
        gcloud services enable run.googleapis.com
        gcloud services enable cloudbuild.googleapis.com
        gcloud services enable vision.googleapis.com
        ```
     4. From cloud console web:
        ```
        Cloud Build > Settings > Service account permissions > Cloud Run Admin role > Enabled
        ```
     6. Build and submit docker image:
        ```
        git clone https://github.com/desendoo/flaskCloudRunAPI.git
        cd flaskCloudRunAPI
        gcloud builds submit --config cloudbuild.yaml .
        ```
     8. Create CLOUD_RUN_ENDPOINT variable to store Cloud Run endpoint:
        ```
        export CLOUD_RUN_ENDPOINT=$(gcloud run services list --platform managed | awk 'NR==2 {print $4}')
        echo $CLOUD_RUN_ENDPOINT
        ```
     9. Check that Cloud Run is working by checking the endpoint link:
        ```
        echo $CLOUD_RUN_ENDPOINT/databasequery
        ```
 5. Create Cloud Functions:
     1. Clone a repository:
         ```
         git clone https://github.com/desendoo/gcsObjectChangesPython.git
         cd gcsObjectChangesPython
         rm -rf .g* README*
         ```
     2. Change the endpoint url in the main.py script:
        ```
        cat main.py | grep "url ="
        sed -i "s|CLOUD_RUN_ENDPOINT|${CLOUD_RUN_ENDPOINT}|" main.py
        cat main.py | grep "url ="
        ```
     4. Deploy Cloud Functions:
        ```
        gcloud functions deploy gcsObjectChangesPython \
            --runtime python39 \
            --entry-point gcsObjectChanges \
            --trigger-resource $PROJECT_ID.appspot.com \
            --trigger-event google.storage.object.finalize \
            --region asia-southeast2
        ```
 6. Test the function by uploading an image to the Storage Bucket—that has been created previously—either via Firebase Console or Google Cloud Console and see the result on the Firebase Storage. Or using this commands:
    ```
    export BUCKET=$(gsutil ls | grep gs://$PROJECT_ID.appspot.com/)
    echo $BUCKET
    wget -c https://img.freepik.com/free-photo/quinoa-mushrooms-lettuce-red-cabbage-spinach-cucumbers-tomatoes-bowl-buddha-dark-top-view_127032-1963.jpg \
        -O demo.jpg
    gsutil cp demo.jpg $BUCKET
    curl "${CLOUD_RUN_ENDPOINT}/query?image=demo.jpg"
    ```
