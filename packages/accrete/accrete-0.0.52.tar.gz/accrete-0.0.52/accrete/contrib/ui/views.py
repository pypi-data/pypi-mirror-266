from django.shortcuts import render


def home(request):
    return render(request, 'ui/layout.html', {})


def form_modal(request):
    return render(request, 'ui/partials/form_modal.html')
