def main():
    print("Hello from crypto!")


if __name__ == "__main__":
    main()



# {% extends 'base.html' %}
# {% block title %}Home - CryptoApp{% endblock %}

# {% block content %}
# <div class="text-center mt-4">
#   <h2>Welcome, {{ user.username }} 👋</h2>
#   <p class="lead">You can buy crypto with Naira via Paystack.</p>
#   <a href="{% url 'logout' %}" class="btn btn-danger mb-4">Logout</a>
# </div>

# <h5>Your Wallet</h5>
# <ul class="list-group mb-4">
#   <li class="list-group-item">BTC: {{ wallet.btc_balance }}</li>
#   <li class="list-group-item">ETH: {{ wallet.eth_balance }}</li>
# </ul>

# <h4>Your Transactions</h4>

# {% if transactions %}
#   <table class="table table-striped mt-3">
#     <thead class="table-dark">
#       <tr>
#         <th>Date</th>
#         <th>Crypto</th>
#         <th>Amount (₦)</th>
#         <th>Status</th>
#         <th>Reference</th>
#       </tr>
#     </thead>
#     <tbody>
#       {% for tx in transactions %}
#       <tr>
#         <td>{{ tx.created_at|date:"M d, Y H:i" }}</td>
#         <td>{{ tx.crypto_symbol }}</td>
#         <td>{{ tx.amount_ngn }}</td>
#         <td>
#           {% if tx.status == "success" %}
#             <span class="badge bg-success">Success</span>
#           {% elif tx.status == "failed" %}
#             <span class="badge bg-danger">Failed</span>
#           {% else %}
#             <span class="badge bg-warning text-dark">Pending</span>
#           {% endif %}
#         </td>
#         <td>{{ tx.reference }}</td>
#       </tr>
#       {% endfor %}
#     </tbody>
#   </table>
# {% else %}
#   <div class="alert alert-info">You have no transactions yet.</div>
# {% endif %}
# {% endblock %}




# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def initialize_paystack(request):
#     """
#     Body JSON: { "amount_ngn": 5000, "crypto_symbol": "BTC" }
#     """
#     user = request.user
#     amount_ngn = int(request.data.get("amount_ngn")) 
#     crypto_symbol = request.data.get("crypto_symbol", "BTC")
#     cmc_url = "https://pro-api.coinmarketcap.com/v1/tools/price-conversion"
#     cmc_params = {"amount": amount_ngn, "symbol": "NGN", "convert": crypto_symbol}
#     cmc_resp = requests.get(cmc_url, params={"amount": amount_ngn, "symbol": "NGN", "convert": crypto_symbol}, headers=CMC_HEADERS)
#     cmc_resp.raise_for_status()
#     cmc_data = cmc_resp.json()
#     try:
#         crypto_amount = Decimal(str(cmc_data["data"]["quote"][crypto_symbol]["price"]))
#     except Exception:
#         crypto_amount = Decimal("0")
#     paystack_url = "https://api.paystack.co/transaction/initialize"
#     headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
#     payload = {
#         "email": user.email,
#         "amount": amount_ngn * 100,  
#         "currency": "NGN",
#         "metadata": {"user_id": user.id, "crypto_symbol": crypto_symbol}
#     }
#     r = requests.post(paystack_url, json=payload, headers=headers, timeout=10)
#     r.raise_for_status()
#     paystack_data = r.json()
#     if not paystack_data.get("status"):
#         return Response({"error":"paystack init failed","details":paystack_data}, status=400)
#     authorization_url = paystack_data["data"]["authorization_url"]
#     ref = paystack_data["data"]["reference"]
#     CryptoTransaction.objects.create(
#         user=user,
#         paystack_ref=ref,
#         amount_ngn=amount_ngn,
#         crypto_symbol=crypto_symbol,
#         crypto_amount=crypto_amount,
#         status="pending"
#     )
#     return Response({"authorization_url": authorization_url, "reference": ref})

