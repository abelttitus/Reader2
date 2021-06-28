
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ccdread.functions.functions import handle_uploaded_file 
from ccdread.functions.card_read import * 
import os

@csrf_exempt
def index(request):
    
    file_pdf=request.FILES['pdf_file']
    handle_uploaded_file(file_pdf)  
    pdf_file_path='ccdread/static/upload/'+file_pdf.name
    package_name= request.POST.get("package_name", "")
    first_page_no= int(request.POST.get("first_page_no", ""))
    last_page_no= int(request.POST.get("last_page_no", ""))
    col_no= int(request.POST.get("col_no", ""))
    excel_file_path=process_pdf(package_name,first_page_no,last_page_no,col_no,pdf_file_path)
    
    with open(excel_file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(excel_file_path)
        return response
    
