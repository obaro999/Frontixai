from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from .models import Business, Service, Appointment

def landing(request):
    return render(request, 'core/landing.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        business_name = request.POST.get('business_name')
        user = User.objects.create_user(username=username, password=password)
        Business.objects.create(user=user, business_name=business_name, slug=username)
        return redirect('/login/')
    return render(request, 'core/register.html')

def business_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            auth_login(request, user)
            return redirect('/dashboard/')
    return render(request, 'core/login.html')

def business_logout(request):
    logout(request)
    return redirect('/')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    business = Business.objects.get(user=request.user)
    appointments = Appointment.objects.filter(business=business, is_cancelled=False).order_by('-created_at')
    return render(request, 'core/dashboard.html', {'business': business, 'appointments': appointments})

def setup_payment(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    business = Business.objects.get(user=request.user)
    if request.method == 'POST':
        business.stripe_key = request.POST.get('stripe_key')
        business.save()
        return redirect('/dashboard/')
    return render(request, 'core/setup_payment.html', {'business': business})

def home(request, username):
    business = Business.objects.get(slug=username)
    return render(request, 'core/login_customer.html', {'business': business})

def book(request, username):
    business = Business.objects.get(slug=username)
    services = Service.objects.filter(business=business)
    if request.method == 'POST':
        service_id = request.POST.get('service')
        date = request.POST.get('date')
        time = request.POST.get('time')
        apt = Appointment.objects.create(
            business=business,
            name=request.session.get('customer_name', ''),
            phone=request.session.get('customer_phone', ''),
            service_id=service_id, date=date, time=time
        )
        return redirect(f'/{username}/payment/?apt={apt.id}')
    return render(request, 'booking/book.html', {'business': business, 'services': services})

def payment(request, username):
    apt_id = request.GET.get('apt')
    appointment = Appointment.objects.get(id=apt_id)
    return render(request, 'booking/payment.html', {'appointment': appointment})

def appointments(request, username):
    business = Business.objects.get(slug=username)
    phone = request.session.get('customer_phone', '')
    apts = Appointment.objects.filter(business=business, phone=phone, is_cancelled=False)
    return render(request, 'booking/appointments.html', {'appointments': apts})

def cancel(request, username):
    if request.method == 'POST':
        apt_id = request.POST.get('apt_id')
        Appointment.objects.filter(id=apt_id).update(is_cancelled=True)
    return redirect(f'/{username}/appointments/')
