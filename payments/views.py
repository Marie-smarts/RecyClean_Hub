from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from .mpesa import MpesaAPI
import json

@login_required
def payment_history_view(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/payment_history.html', {'payments': payments})


@login_required
def initiate_payment_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = int(data.get('amount'))
            phone = data.get('phone')
            payment_type = data.get('payment_type', 'recycler_earning')
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                phone_number=phone,
                payment_type=payment_type,
                status='processing'
            )
            
            # Initialize M-Pesa
            mpesa = MpesaAPI()
            
            # Initiate STK Push
            result = mpesa.stk_push(
                phone_number=phone,
                amount=amount,
                account_reference=f"PAY{payment.id}",
                transaction_desc="EcoRecycle Payment"
            )
            
            if result.get('ResponseCode') == '0':
                payment.mpesa_code = result.get('CheckoutRequestID', '')
                payment.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Payment initiated! Check your phone for M-Pesa prompt.'
                })
            else:
                payment.status = 'failed'
                payment.save()
                return JsonResponse({
                    'success': False,
                    'error': result.get('errorMessage', 'Payment failed')
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa callback"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extract transaction details
            result_code = data['Body']['stkCallback']['ResultCode']
            checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']
            
            # Find payment
            payment = Payment.objects.filter(mpesa_code=checkout_request_id).first()
            
            if payment:
                if result_code == 0:
                    # Success
                    payment.status = 'completed'
                    callback_metadata = data['Body']['stkCallback'].get('CallbackMetadata', {})
                    for item in callback_metadata.get('Item', []):
                        if item['Name'] == 'MpesaReceiptNumber':
                            payment.mpesa_code = item['Value']
                            break
                else:
                    # Failed
                    payment.status = 'failed'
                
                payment.save()
            
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
        except Exception as e:
            return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})
    
    return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid request'})