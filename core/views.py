from django.shortcuts import render, redirect
from .models import Appointment, BusinessConfig
import africastalking

AT_USERNAME = "sandbox"
AT_API_KEY = "atsk_8da4c7433d5b213a9e15e59f7d54be971b2c43094e40ea6f2b985d49cc270430e09dc988"

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS

def send_sms(phone, message):
    try:
        number = "+234" + phone.replace(" ", "")[-10:]
        sms.send(message, [number])
    except Exception as e:
        print("SMS error: " + str(e))

def home(request):
    name = request.GET.get('name', '').strip()
    phone = request.GET.get('phone', '').strip()
    if name and phone:
        is_returning = Appointment.objects.filter(phone=phone).exists()
        return render(request, 'core/home.html', {
            'name': name,
            'phone': phone,
            'is_returning': is_returning
        })
    return render(request, 'core/login.html')

def book(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        Appointment.objects.create(name=name, phone=phone, date=date, time=time)
        send_sms(phone, "Hi " + name + ", your appointment on " + date + " at " + time + " is confirmed. - Frontix Ai")
        return render(request, 'core/booked.html', {'name': name, 'date': date, 'time': time})
    return render(request, 'core/book.html')

def appointments(request):
    phone = request.GET.get('phone', '').strip()
    items = Appointment.objects.filter(phone=phone, is_cancelled=False)
    return render(request, 'core/appointments.html', {'appointments': items, 'phone': phone})

def cancel(request):
    if request.method == 'POST':
        appt_id = request.POST.get('appt_id')
        phone = request.POST.get('phone')
        appt = Appointment.objects.get(id=appt_id)
        appt.is_cancelled = True
        appt.save()
        send_sms(phone, "Your appointment on " + appt.date + " at " + appt.time + " has been cancelled. - Frontix Ai")
        return redirect('/appointments/?phone=' + phone)
    return redirect('/')

def payment(request):
    config = BusinessConfig.objects.first()
    return render(request, 'core/payment.html', {'config': config})

def admin_dashboard(request):
    appointments = Appointment.objects.filter(is_cancelled=False).order_by('-created_at')
    return render(request, 'core/admin_dashboard.html', {'appointments': appointments})