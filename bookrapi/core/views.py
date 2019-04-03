from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView

from .models import BookrDocument, BookrChunkedUpload


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class BookrChunkedUploadView(ChunkedUploadView):

    model = BookrChunkedUpload

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass
        
@method_decorator(csrf_exempt, name='dispatch')
class BookrChunkedUploadCompleteView(ChunkedUploadCompleteView):

    model = BookrChunkedUpload

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def on_completion(self, uploaded_file, request):
        # Do something with the uploaded file. E.g.:
        # * Store the uploaded file on another model:
        BookrDocument.objects.create(file=uploaded_file)
        # * Pass it as an argument to a function:
        # function_that_process_file(uploaded_file)
        pass

    def get_response_data(self, chunked_upload, request):
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (chunked_upload.filename, chunked_upload.offset))}