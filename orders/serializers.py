from rest_framework import serializers
from .models import Order, OrderItem, Payment, GiftCard

class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = ['id', 'customer', 'card_number', 'initial_amount', 'balance', 'is_active', 'expiry_date', 'created_at']
        read_only_fields = ['card_number', 'balance', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderItem
        # 🌟 تم حذف processing_start_at و ready_at لأنها تتبع الطلب (Order) وليس القطعة (Item) 🌟
        fields = ['id', 'order', 'item', 'item_name', 'status_display', 'quantity', 'price', 'is_express', 'status']
        extra_kwargs = {'order': {'required': False}}

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['method', 'amount']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payments = PaymentSerializer(many=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True, default='Walking Customer')
    customer_phone = serializers.CharField(source='customer.phone', read_only=True, default='---')
    # 🌟 تصحيح: سحب حقل نص الفئة مباشرة من بروفايل العميل
    customer_category = serializers.CharField(source='customer.customer_category', read_only=True, default='Uncategorized')
    customer_file_number = serializers.CharField(source='customer.file_number', read_only=True, default='---')
    payment_status = serializers.SerializerMethodField()
    gift_card_number = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'branch', 'customer', 'customer_name', 'customer_phone', 'customer_category', 
            'customer_file_number', 'total_amount', 'discount_percentage', 'remarks', 'reference', 
            'items', 'payments', 'created_at', 'delivery_date', 'gift_card_number',
            'processing_type', 'logistics_type', 'status', 'payment_status', 
            'processing_start_at', 'ready_at', 'is_void'
        ]

    def get_payment_status(self, obj):
        total_paid = sum(p.amount for p in obj.payments.all())
        return 'PAID' if total_paid >= obj.total_amount else 'PENDING'

    def create(self, validated_data):
        gift_card_number = validated_data.pop('gift_card_number', None)
        items_data = validated_data.pop('items')
        payments_data = validated_data.pop('payments')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        for payment_data in payments_data:
            method = payment_data.get('method')
            amount = payment_data.get('amount')
            if method == 'GIFT_CARD' and gift_card_number:
                gc = GiftCard.objects.get(card_number=gift_card_number, is_active=True)
                gc.balance -= amount
                if gc.balance <= 0: gc.is_active = False
                gc.save()
            elif method == 'WALLET' and order.customer:
                order.customer.wallet_balance -= amount
                order.customer.save()
            Payment.objects.create(order=order, **payment_data)
        return order