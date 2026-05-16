from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.text import slugify
from .models import Business, BusinessConfig, Appointment
import africastalking
import os

africastalking.initialize(
    username=os.environ.get('AT_USERNAME', 'sandbox'),
    api_key=os.environ.get('AT_API_KEY', '')
)
sms = africastalking.SMS


def send_sms(phone, message):
    try:
        sms.send(message, [f"+{phone.lstrip('+').lstrip('0')}"])
    except Exception as e:
        print(f"SMS error: {e}")


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        business_name = request.POST.get('business_name', '').strip()

        if not username or not password or not business_name:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'register.html')

        base_slug = slugify(business_name)
        slug = base_slug
        counter = 1
        while Business.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        user = User.objects.create_user(username=username, password=password)
        business = Business.objects.create(owner=user, name=business_name, slug=slug)
        BusinessConfig.objects.create(
            business=business,
            business_name=business_name,
            bank_name='',
            account_number='',
            account_name='',
            support_phone=''
        )

        login(request, user)
        return redirect('dashboard')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    business = request.user.business
    appointments = Appointment.objects.filter(
        business=business, is_cancelled=False
    ).order_by('-date', '-time')
    return render(request, 'dashboard.html', {
        'business': business,
        'appointments': appointments
    })


def book_appointment(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        date = request.POST.get('date', '').strip()
        time = request.POST.get('time', '').strip()

        if not all([name, phone, date, time]):
            messages.error(request, 'All fields are required.')
            return render(request, 'book.html', {'business': business})

        Appointment.objects.create(
            business=business,
            name=name,
            phone=phone,
            date=date,
            time=time
        )

        send_sms(
            phone,
            f"Hi {name}, your appointment with {business.name} is confirmed for {date} at {time}. - Frontix AI"
        )

        return redirect('payment_info', business_id=business.id)

    return render(request, 'book.html', {'business': business})


def payment_info(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    config = get_object_or_404(BusinessConfig, business=business)
    return render(request, 'payment.html', {
        'business': business,
        'config': config
    })


@login_required
def cancel_appointment(request, appointment_id):
    business = request.user.business
    appointment = get_object_or_404(Appointment, id=appointment_id, business=business)
    appointment.is_cancelled = True
    appointment.save()
    send_sms(
        appointment.phone,
        f"Hi {appointment.name}, your appointment with {business.name} on {appointment.date} at {appointment.time} has been cancelled. - Frontix AI"
    )
    return redirect('dashboard')


@login_required
def update_payment_info(request):
    business = request.user.business
    config = business.config
    if request.method == 'POST':
        config.bank_name = request.POST.get('bank_name', '').strip()
        config.account_number = request.POST.get('account_number', '').strip()
        config.account_name = request.POST.get('account_name', '').strip()
        config.support_phone = request.POST.get('support_phone', '').strip()
        config.save()
        messages.success(request, 'Payment info updated.')
        return redirect('dashboard')
    return render(request, 'setup_payment.html', {'config': config, 'business': business})