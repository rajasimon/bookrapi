import os

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import BookrDocument


def get_chunk_name(uploaded_filename, chunk_number):
    return uploaded_filename + "_part_{}".format(chunk_number)


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class Upload(View):
    def get(self, request, *args, **kwargs):
        resumableIdentfier = request.GET.get('resumableIdentifier', None)
        resumableFilename = request.GET.get('resumableFilename', None)
        resumableChunkNumber = request.GET.get('resumableChunkNumber', None)

        if not resumableIdentfier or not resumableFilename or not resumableChunkNumber:
        # Parameters are missing or invalid
            raise Exception('Parameter error')

        # chunk folder path based on the parameters
        temp_dir = os.path.join(settings.MEDIA_ROOT, resumableIdentfier)

        # chunk path based on the parameters
        chunk_file = os.path.join(temp_dir, get_chunk_name(resumableFilename, resumableChunkNumber))

        if os.path.isfile(chunk_file):
            # Let resumable.js know this chunk already exists
            return HttpResponse('Ok')
        else:
            # Let resumable.js know this chunk does not exists and needs to be uploaded
            return HttpResponseBadRequest('Not found')

    def post(self, request, *args, **kwargs):
        resumableTotalChunks = request.POST.get('resumableTotalChunks', None)
        resumableChunkNumber = request.POST.get('resumableChunkNumber', 1)
        resumableFilename = request.POST.get('resumableFilename', 'error')
        resumableIdentfier = request.POST.get('resumableIdentifier', 'error')

        # get the chunk data
        chunk_data = request.FILES['file']

        # make our temp directory
        temp_dir = os.path.join(settings.MEDIA_ROOT, resumableIdentfier)
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir, mode=0o777)

        # save the chunk data
        chunk_name = get_chunk_name(resumableFilename, resumableChunkNumber)
        chunk_file = os.path.join(settings.MEDIA_ROOT, chunk_name)
        path = default_storage.save(chunk_file, ContentFile(chunk_data.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        # chunk_data.save(chunk_file.encode())

        # check if the upload is complete
        chunk_paths = [os.path.join(settings.MEDIA_ROOT, get_chunk_name(resumableFilename, x)) for x in range(1, int(resumableTotalChunks)+1)]
        upload_complete = all([os.path.exists(p) for p in chunk_paths])

        # combine all the chunks to create the final file
        if upload_complete:
            target_file_name = os.path.join(settings.MEDIA_ROOT, resumableFilename)
            with open(target_file_name, "ab") as target_file:
                for p in chunk_paths:
                    stored_chunk_file_name = p
                    stored_chunk_file = open(stored_chunk_file_name, 'rb')
                    target_file.write(stored_chunk_file.read())
                    stored_chunk_file.close()
                    os.unlink(stored_chunk_file_name)
            target_file.close()
            os.rmdir(temp_dir)

            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "chat_stream", 
                {
                    "type": "stream_message", 
                    "message": {'isCompleted': True, "result": "This file saved in db success"},
                }
            )

        return HttpResponse('Chunk Uploaded')
