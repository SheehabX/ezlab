from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
import numpy as np
import argparse
import cv2
import matplotlib.pyplot as plt
import os


# Create your views here.

def index(request):
    if request.method == 'POST' and request.FILES['colony_image']:
        
        min_distance = request.POST.get('min_distance', None)
        colony_image = request.FILES['colony_image']
        
        fs = FileSystemStorage()
        filename = fs.save(colony_image.name, colony_image)
        uploaded_file_url = fs.url(filename)
        
        colonies = analyse(filename, min_distance)
        return render(request, 'quantifier.html', {
            'uploaded_file_url': uploaded_file_url, 'min_distance': min_distance, 'colonies': colonies
        })

    return render(request, 'quantifier.html')


def analyse(image, distance):
    
    # load the image and perform pyramid mean shift filtering
    # to aid the thresholding step

    image = cv2.imread(os.path.join(settings.MEDIA_ROOT, image))
    shifted = cv2.pyrMeanShiftFiltering(image, 21, 51)

    # convert the mean shift image to grayscale, then apply
    # Otsu's thresholding
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # compute the exact Euclidean distance from every binary
    # pixel to the nearest zero pixel, then find peaks in this
    # distance map
    D = ndimage.distance_transform_edt(thresh)
    localMax = peak_local_max(D, indices=False, min_distance=int(distance), labels=thresh)

    # perform a connected component analysis on the local peaks,
    # using 8-connectivity, then appy the Watershed algorithm
    markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
    labels = watershed(-D, markers, mask=thresh)
    #print("[INFO] {} unique segments found".format(len(np.unique(labels)) - 1))

    return (len(np.unique(labels)) - 1)