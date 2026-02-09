from django.urls import path
from .views import UploadCSV, Summary, History, PDFReport
urlpatterns = [
    path('upload/', UploadCSV.as_view(), name='upload'),
    path('summary/', Summary.as_view(), name='summary'),
    path('history/', History.as_view(), name='history'),
    path('pdf/', PDFReport.as_view(), name='pdf')
]