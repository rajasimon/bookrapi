from django.urls import path

from .views import BookrChunkedUploadView, BookrChunkedUploadCompleteView

urlpatterns = [
    path('upload/', BookrChunkedUploadView.as_view()),
    path('upload_complete/', BookrChunkedUploadCompleteView.as_view())
]
