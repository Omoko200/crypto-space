from . import cmc

@login_required
def home_view(request):
    from .models import Transaction
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    try:
        btc_price = cmc.get_crypto_price('BTC', 'NGN')
        eth_price = cmc.get_crypto_price('ETH', 'NGN')
    except Exception:
        btc_price = eth_price = 'Unavailable'

    return render(request, 'home.html', {
        'user': request.user,
        'transactions': transactions,
        'btc_price': btc_price,
        'eth_price': eth_price,
    })



