from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')

def evaluaciones(request):
    return render(request, 'evaluaciones.html')

def aprobaciones(request):
    return render(request, 'aprobaciones.html')

def reportes(request):
    return render(request, 'reportes.html')

def bonos(request):
    return render(request, 'bonos.html')

def usuarios(request):
    return render(request, 'usuarios.html')