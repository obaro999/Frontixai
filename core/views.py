from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.contrib.auth.models import User
from .models import Business, BusinessConfig, Appointment
import africastalking

africastalking.initialize('frontixai', 'YOUR_API_KEY')
sms = africastalking.SMS

def send_sms(phone, message):
    try:
        number = '+234' + phone.replace(' ', '')[1:]
        sms.send(message, [number])
    except Exception as e:
        print('SMS error: ' + str(e))

def landing(request):
    return render(request, 'core/landing.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone')

        user = User.objects.create_user(username=username, password=password)
        slug = slugify(username)
        Business.objects.create(owner=user, name=business_name, slug=slug)
        login(request, user)
        return redirect('/dashboard/')
    return render(request, 'core/register.html')

def business_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/dashboard/')
    return render(request, 'core/login.html')

def business_logout(request):
    logout(request)
    return redirect('/')

@login_required
def dashboard(request):
    business = Business.objects.get(owner=request.user)
    appointments = Appointment.objects.filter(business=business, is_cancelled=False).order_by('-created_at')
    return render(request, 'core/dashboard.html', {'appointments': appointments, 'business': business})

@login_required
def setup_payment(request):
    business = Business.objects.get(owner=request.user)
    if request.method == 'POST':
        config, _ = BusinessConfig.objects.get_or_create(business=business)
        config.bank_name = request.POST.get('bank_name')
        config.account_number = request.POST.get('account_number')
        config.account_name = request.POST.get('account_name')
        config.support_phone = request.POST.get('support_phone')
        config.business_name = business.name
        config.save()
        return redirect('/dashboard/')
    return render(request, 'core/setup_payment.html')

def home(request, username):
    try:
        user = User.objects.get(username=username)
        business = Business.objects.get(owner=user)
    except:
        return redirect('/')
    name = request.GET.get('name', '').strip()
    phone = request.GET.get('phone', '').strip()
    is_returning = Appointment.objects.filter(phone=phone, business=business).exists()
    if name and phone:
        return render(request, 'core/home.html', {'name': name, 'phone': phone, 'is_returning': is_returning, 'business': business})
    return render(request, 'core/customer.html', {'business': business})

def book(request, username):
    user = User.objects.get(username=username)
    business = Business.objects.get(owner=user)
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        Appointment.objects.create(business=business, name=name, phone=phone, date=date, time=time)
        send_sms(phone, 'Hi ' + name + ', your appointment on ' + date + ' at ' + time + ' is confirmed. - ' + business.name)
        return redirect('/' + username + '/payment/')
    return render(request, 'core/book.html', {'business': business})

def payment(request, username):
    user = User.objects.get(username=username)
    business = Business.objects.get(owner=user)
    config = BusinessConfig.objects.filter(business=business).first()
    return render(request, 'core/payment.html', {'config': config, 'business': business})

def appointments(request, username):
    user = User.objects.get(username=username)
    business = Business.objects.get(owner=user)
    phone = request.GET.get('phone', '').strip()
    items = Appointment.objects.filter(business=business, phone=phone, is_cancelled=False)
    return render(request, 'core/appointments.html', {'appointments': items, 'phone': phone, 'business': business})

def cancel(request, username):
    user = User.objects.get(username=username)
    business = Business.objects.get(owner=user)
    if request.method == 'POST':
        appt_id = request.POST.get('appt_id')
        appt = Appointment.objects.get(id=appt_id)
        appt.is_cancelled = True
        appt.save()
        send_sms(appt.phone, 'Your appointment on ' + appt.date + ' at ' + appt.time + ' has been cancelled. - ' + business.name)
        return redirect('/' + username + '/appointments/?phone=' + appt.phone) 