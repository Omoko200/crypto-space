from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

import os, requests, json
from decimal import Decimal

from .models import Wallet, CryptoTransaction


CMC_HEADERS = {"X-CMC_PRO_API_KEY": settings.COINMARKETCAP_API_KEY}
COINMARKETCAP_API_KEY = "e3b04a639236435293d55e150032362b"
PAYSTACK_SECRET_KEY = "sk_test_cc1ef244f2578a107ea88951528438d9d601b415"

@api_view(["GET"])
@permission_classes([AllowAny])
def price_quote(request):
    """
    Proxy coinmarketcap price conversion.
    Query params: symbol=BTC&convert=NGN
    """
    symbol = request.GET.get("symbol", "BTC")
    convert = request.GET.get("convert", "NGN")
    url = "https://pro-api.coinmarketcap.com/v1/tools/price-conversion"
    params = {"amount": 1, "symbol": symbol, "convert": convert}
    r = requests.get(url, params=params, headers=CMC_HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_paystack(request):
    """
    Initialize a Paystack transaction for buying crypto.
    Expects POST fields:
      - crypto (e.g. 'BTC' or 'ETH')
      - amount (NGN as string or number, e.g. "5000" or "5000.00")
    Returns:
      - redirect to Paystack payment page on success
      - JSON error on failure (helpful when invoked via AJAX)
    """
    if not PAYSTACK_SECRET_KEY:
        return JsonResponse({"error": "Paystack secret key not configured."}, status=500)

    crypto = request.POST.get("crypto")
    amount_raw = request.POST.get("amount")

    if not crypto:
        return JsonResponse({"error": "Missing 'crypto' field."}, status=400)
    if not amount_raw:
        return JsonResponse({"error": "Missing 'amount' field."}, status=400)

    try:
        amount_naira = Decimal(amount_raw)
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({"error": "Invalid amount format."}, status=400)

    MIN_NGN = Decimal("100") 
    if amount_naira < MIN_NGN:
        return JsonResponse({"error": f"Minimum amount is ₦{MIN_NGN}."}, status=400)

    try:
        amount_kobo = int(amount_naira * 100) 
    except (TypeError, InvalidOperation) as e:
        return JsonResponse({"error": "Could not convert amount to kobo."}, status=400)

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": request.user.email if request.user.is_authenticated else "no-reply@example.com",
        "amount": amount_kobo,
        "callback_url": request.build_absolute_uri("/paystack/callback/"),
        "metadata": {
            "crypto": crypto,
            "user_id": request.user.id if request.user.is_authenticated else None
        }
    }
    res = requests.post(url, json=payload, headers=headers, timeout=20)
    try:
        res_json = res.json()
    except ValueError:
        return JsonResponse({"error": "Invalid response from Paystack."}, status=502)

    if not res_json.get("status"):
        message = res_json.get("message") or res_json.get("data", {}).get("message") or "Paystack initialization failed."
        return JsonResponse({"error": message, "raw": res_json}, status=400)

    
    paystack_data = res_json["data"]
    authorization_url = paystack_data.get("authorization_url")
    reference = paystack_data.get("reference")

    try:
        tx = CryptoTransaction.objects.create(
            user=request.user,
            paystack_ref=reference,
            amount_ngn=amount_naira,
            crypto_symbol=crypto,
            crypto_amount=Decimal("0"),
            status="pending",
        )
    except Exception as e:
        
        return JsonResponse({"error": "Could not create transaction record.", "details": str(e)}, status=500)

    
    if authorization_url:
        return redirect(authorization_url)
    else:
        return JsonResponse({"error": "No authorization URL returned by Paystack.", "raw": res_json}, status=500)


@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    data = json.loads(payload)
    event = data.get("event")
    if event != "charge.success":
        return Response({"status": "ignored"}, status=200)
    ref = data["data"]["reference"]
    verify_url = f"https://api.paystack.co/transaction/verify/{ref}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    v = requests.get(verify_url, headers=headers, timeout=10)
    v.raise_for_status()
    verified = v.json()
    if verified.get("data", {}).get("status") == "success":
        tx = CryptoTransaction.objects.filter(paystack_ref=ref).first()
        if tx and tx.status != "success":
            tx.status = "success"
            tx.save()
            wallet, _ = Wallet.objects.get_or_create(user=tx.user)
            if tx.crypto_symbol.upper() == "BTC":
                wallet.btc_balance += tx.crypto_amount
            elif tx.crypto_symbol.upper() == "ETH":
                wallet.eth_balance += tx.crypto_amount
            wallet.save()
    return Response({"status": "ok"}, status=200)


def complete_transaction(request, crypto_symbol, amount_crypto, amount_naira):
    wallet = Wallet.objects.get(user=request.user)

    # Create transaction
    Transaction.objects.create(
        user=request.user,
        crypto_symbol=crypto_symbol,
        amount_crypto=Decimal(amount_crypto),
        amount_naira=Decimal(amount_naira),
    )

    # Update wallet balance
    if crypto_symbol == 'BTC':
        wallet.btc_balance += Decimal(amount_crypto)
    elif crypto_symbol == 'ETH':
        wallet.eth_balance += Decimal(amount_crypto)

    wallet.save()



@csrf_exempt
def paystack_callback(request):
    reference = request.GET.get('reference') or request.GET.get('trxref')
    if not reference:
        return render(request, 'error.html', {'message': 'No payment reference found'})

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    response = requests.get(url, headers=headers)
    result = response.json()

    if result['data']['status'] == 'success':
        user = request.user
        amount_naira = Decimal(result['data']['amount']) / 100  
        crypto_symbol = result['data']['metadata']['crypto_symbol']
        amount_crypto = Decimal(result['data']['metadata']['amount_crypto'])

        
        wallet, created = Wallet.objects.get_or_create(user=user)

    
        transaction, created = CryptoTransaction.objects.get_or_create(
            reference=reference,
            defaults={
                'user': user,
                'crypto_symbol': crypto_symbol,
                'amount_crypto': amount_crypto,
                'amount_naira': amount_naira,
                'status': 'completed',
            }
        )

        
        if created:
            if crypto_symbol == 'BTC':
                wallet.btc_balance += amount_crypto
            elif crypto_symbol == 'ETH':
                wallet.eth_balance += amount_crypto
            wallet.save()

        return redirect('home') 

    else:
        return render(request, 'error.html', {'message': 'Payment verification failed.'})

def paystack_callback(request):
    """
    Handles Paystack callback after payment.
    """
    reference = request.GET.get('reference')
    if not reference:
        return HttpResponse("Invalid callback: missing reference.", status=400)

    try:
        transaction = CryptoTransaction.objects.get(paystack_ref=reference)
        transaction.status = "success"
        transaction.save()
        return redirect("home")
    except CryptoTransaction.DoesNotExist:
        return HttpResponse("Transaction not found.", status=404)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password1', '').strip()


        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')



@login_required
def home(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    cryptotransactions = CryptoTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home.html', {'wallet': wallet, 'cryptotransactions': cryptotransactions})
# def home(request):
#     wallet, created = Wallet.objects.get_or_create(user=request.user)
#     return render(request, 'home.html', {'wallet': wallet})





def logout_view(request):
    auth_logout(request)
    return redirect('login')


# Create your views here.
