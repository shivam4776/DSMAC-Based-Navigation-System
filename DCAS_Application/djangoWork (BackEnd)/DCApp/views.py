from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import main  # Import the function


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the file to the backend storage
        global file_path
        file_path = default_storage.save(file.name, file)
        return Response({"message": "File uploaded successfully", "file_path": file_path}, status=status.HTTP_201_CREATED)

@csrf_exempt
def process_options(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            overlapping = data.get("option1")
            imgQuality = data.get("option2")
            # print('Overlapping',type(overlapping))
            # print('imgQuality',type(imgQuality))
            print('file_path',file_path)

            # Pass the values to a function in utils.py
            main(overlapping, imgQuality, file_path)

            return JsonResponse({"message": "Options received successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)