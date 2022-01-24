from django.shortcuts import render
from .forms import ImageForm, LogoForm
from io import StringIO, BytesIO
from PIL import Image
import base64
import cv2
import numpy as np
from django.core.files.base import ContentFile
from django.views import View, generic 
import datetime

def gray_a(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray

def naklon(img):
    rows,cols,ch = img.shape
    pts1x = np.float32([[0,0],[640,360],[1280,640]])
    pts2x = np.float32([[30,30],[640,360],[1270,630]])
    Mx = cv2.getAffineTransform(pts1x,pts2x)
    dstx = cv2.warpAffine(img,Mx,(cols,rows))
    return dstx 

def rot(img, x):
    if x == 1:
        img_rot = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif x == 2:
        img_rot = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif x == 3:
        img_rot = cv2.rotate(img, cv2.ROTATE_180)
    return img_rot

def thres_a(img):
    # gray treshold
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # treshold
    ret, thres = cv2.threshold(img, 130,220, cv2.THRESH_BINARY)
    # treshold + filtr
    thres_filtr = cv2.bilateralFilter(thres, 7, 120, 120)
    return thres_filtr

def gray_thres(img, x):
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, img = cv2.threshold(img, x, 250, cv2.THRESH_BINARY)
    return img

def col_thres(img, x):
    #img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    ret, img = cv2.threshold(img, x, 250, cv2.THRESH_BINARY)
    return img

def res(img, value):
    k = (1/img.shape[1])*value
    img = cv2.resize(img, (int(img.shape[1]*k), int(img.shape[0]*k)))
    return img

def logos(img, logo, perc):
    # I want to put logo on top-left corner, So I create a ROI
    rows,cols,channels = logo.shape
    y, x, ch = img.shape
    y_perc = int(y*perc[1]/100)
    x_perc = int(x*perc[0]/100)
    roi = img[y_perc:y_perc+rows, x_perc:x_perc+cols ]
    # Now create a mask of logo and create its inverse mask also
    logo_gray = cv2.cvtColor(logo,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(logo_gray, 240, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)
    # Now black-out the area of logo in ROI
    img_bg = cv2.bitwise_and(roi,roi,mask = mask)
    # Take only region of logo from logo image.
    logo_fg = cv2.bitwise_and(logo,logo,mask = mask_inv)
    # Put logo in ROI and modify the main image
    dst = cv2.add(img_bg,logo_fg)
    img[y_perc:y_perc+rows, x_perc:x_perc+cols ]= dst
    return img

def uvod(request):
    return render(request, 'foto/uvod.html')

def pg2(request):
    if request.method == "POST":
        form = LogoForm(request.POST, request.FILES)
        if form.is_valid():
            image_field = form.cleaned_data['image']
            img = Image.open(image_field.file)
            img = np.array(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            logo_field = form.cleaned_data['logo']
            logo = Image.open(logo_field.file)
            logo = np.array(logo)
            logo = cv2.cvtColor(logo, cv2.COLOR_RGB2BGR)
            x = int(request.POST.get('x'))
            y = int(request.POST.get('y'))
            #x = form.cleaned_data['x']
            #y = form.cleaned_data['y']
            try:
                img = logos(img, logo, [x,y] )
                # resize
                if request.POST.get("format")=="1":
                    img = res(img, 320)
                elif request.POST.get("format")=="2":
                    img = res(img, 640)
                elif request.POST.get("format")=="3":
                    img = res(img, 1280)
                elif request.POST.get("format")=="4":
                    img = res(img, 1920)
                ret, img = cv2.imencode('.jpg', img)
                img = base64.b64encode(img).decode('ascii')

                return render(request, 'foto/pg2.html', dict(form=form, img=img))
            except:
                return render(request, 'foto/pg2.html', dict(form=form, err="zmente umisteni, logo se nevejde do obrazku!"))

    else:
        form = LogoForm()
    return render(request, 'foto/pg2.html', dict(form=form, img=''))

class Upload(generic.edit.CreateView):
    form_class = ImageForm
    def get(self, request):
        form = self.form_class(None)
        return render(request, 'foto/index.html', {"form":form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(commit=True)
        return render(request, 'foto/index.html', {"form":form})

class Obrazek(View):
    def pg1(request):
        start = datetime.datetime.now()
        """Process images uploaded by users"""
        if request.method == 'POST':
            form = ImageForm(request.POST, request.FILES)  
            if form.is_valid():    
                #name_field = form.cleaned_data['title']
                image_field = form.cleaned_data['image']

                x = Image.open(image_field.file)
                x = np.array(x)
                x = cv2.cvtColor(x, cv2.COLOR_RGB2BGR)
                
                if request.POST.get("format")=="1":
                    x = res(x, 320)
                elif request.POST.get("format")=="2":
                    x = res(x, 640)
                elif request.POST.get("format")=="3":
                    x = res(x, 1280)
                elif request.POST.get("format")=="4":
                    x = res(x, 1920)
                elif request.POST.get("format_self")!="0":
                    x = res(x, int(request.POST.get("format_self")))
                # resize to small
                else:
                    if int(x.shape[1]) > 320:
                        percW = (1/int(x.shape[1])*640)
                    else:
                        percW = x.shape[1]
                    if int(x.shape[0]) > 320:
                        percH = (1/int(x.shape[0])*640)
                    else:
                        percH = x.shape[0]
                    perc = min(percW, percH)
                    x = cv2.resize(x, (int(x.shape[1]*perc), int(x.shape[0]*perc)))
                # openCV to base64  
                origin = x
                ret, origin = cv2.imencode('.jpg', x)
                origin = base64.b64encode(origin).decode('ascii')

                # gray image
                if request.POST.get("uprava")=="1":
                    img = gray_a(x)  
                # threshold
                elif request.POST.get("uprava")=="2":
                    img = gray_thres(x, int(request.POST.get("gray_vol")))
                # threshold_barvy
                elif request.POST.get("uprava")=="7":
                    img = col_thres(x, int(request.POST.get("col_vol")))
                # naklon
                elif request.POST.get("uprava")=="3":
                    img = naklon(x)
                # rotation
                elif request.POST.get("uprava")=="4":
                    img = rot(x,1)
                elif request.POST.get("uprava")=="5":
                    img = rot(x,2)
                elif request.POST.get("uprava")=="6":
                    img = rot(x,3)
                else:
                    img = x
                '''    
                origin = x
                ret, origin = cv2.imencode('.jpg', x)
                origin = base64.b64encode(origin).decode('ascii')
                '''
                ret, img = cv2.imencode('.jpg', img)
                img = base64.b64encode(img).decode('ascii')

                print(datetime.datetime.now()-start)
                return render(request, 'foto/pg1.html', dict(form=form, origin=origin, img = img))

        else:
            form = ImageForm()
        return render(request, 'foto/pg1.html', dict(form=form, origin="", img=""))
'''  
    
            s = image_field.file
            se = Image.open(s)
            se = np.array(se)
            se = cv2.cvtColor(se, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(se, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (int(se.shape[1]*0.4), int(se.shape[0]*0.4)))
            cv2.imwrite("C:\\naucse-python\\ITNet\\Django\\mojestranky\\foto\\static\\foto\\gray.jpg", gray)

            se = cv2.cvtColor(se, cv2.COLOR_BGR2GRAY)
            ret, thres = cv2.threshold(se, 140, 220, cv2.THRESH_BINARY)          
            thres = cv2.resize(thres, (int(se.shape[1]*0.4), int(se.shape[0]*0.4)))
            cv2.imwrite("C:\\naucse-python\\ITNet\\Django\\mojestranky\\foto\\static\\foto\\thres.jpg", thres)

            #image_file = StringIO(image_field.read())
            #image = Image.open(image_file)
            # Get the current instance object to display in the template
            img_obj = form.instance
            img_gray = "foto\\gray.jpg"
            img_thres = "foto\\thres.jpg"
            return render(request, 'foto/index.html', dict(form=form, img_obj=img_obj, img_gray = img_gray, img_thres = img_thres, gray = gray))
    else:
        form = ImageForm()
    return render(request, 'foto/index.html', dict(form=form))

    '''
    

  

