from django.http import HttpResponse


def contact(request):
    return HttpResponse("hello")


def price_list(request):
    return HttpResponse("price list")


def projects(request):
    return HttpResponse("projects")


def services(request):
    return HttpResponse("services")


def team(request):
    return HttpResponse("team")
