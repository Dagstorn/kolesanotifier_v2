from django.shortcuts import render, redirect, reverse
from .models import Filter, Car
from django.http import JsonResponse, HttpResponse

def index(request):
    filters = Filter.objects.all()
    context = {
        'filters':filters,
    }
    return render(request, 'handler/index.html', context)

def kolesafilters(request):
    filters = Filter.objects.all()
    data = {}
    for f in filters:
        data[f.id] = {
            'title':f.title,
            'url':f.url,
            'lastcar':f.lastcar,
            'cheap_perc':f.cheaper_perc,
            'view_count':f.view_count
        }
    return JsonResponse(data)

def get_cars(request, f_key):
    try:
        filter = Filter.objects.get(id=f_key)
    except:
        return JsonResponse({'error': 'Filter with such key does not exist'}, status=400)
    
    cars = filter.saved_cars.all()
    return JsonResponse([c.key for c in cars], safe=False)

def add_car(request, f_key):
    print("add car")
    print(request.method)
    if request.method == 'POST':
        try:
            key = request.POST.get('key')
            filter = Filter.objects.get(id=f_key)
            print(f"creating new obj with key {key}")

            Car.objects.create(
                filter = filter,
                key = key
            )
            print("created car")

            cars = Car.objects.all()
            print(cars)
            return HttpResponse()
        except:
            return JsonResponse({'error': 'Missing required parameter "key"'}, status=400)
    else:
        return render(request, 'handler/addcar.html', {})


def updatelastcar(request):
    if request.method == 'POST':
        lastcar_from_post = request.POST.get('lcid')
        fid = request.POST.get('fid')
        try:
            current_filter = Filter.objects.get(id=fid)
        except:
            current_filter = None
        if current_filter:
            current_filter.lastcar = lastcar_from_post
            current_filter.save()
        return HttpResponse()
    else:
        return render(request, 'handler/lastcar.html', {})
    