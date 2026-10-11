from django.http import HttpResponse
from django.shortcuts import render


def contact(request):
    return HttpResponse("contact")


def price_list(request):
    return HttpResponse("price list")


def projects(request):
    return HttpResponse("projects")


def services(request):
    return HttpResponse("services")


def team(request):
    return HttpResponse("team")
