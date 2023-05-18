from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from .models import Cart, CartItem, Customer, Order, OrderItem, Product,Collection, ProductImage,Review
from .signals import order_created


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title','products_count',]

    products_count = serializers.IntegerField()

class ProductImageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        product_id = self.context['product_id']

        return ProductImage.objects.create(product_id = product_id , **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many = True ,read_only = True)
    class Meta:
        model = Product
        fields =['id','title','slug','inventory','unit_price','price_with_tax','collection','images']

    # id =serializers.IntegerField()
    # title =serializers.CharField(max_length=255)
    # price = serializers.DecimalField(max_digits=6,decimal_places=2,source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    # # collection = serializers.PrimaryKeyRelatedField(queryset = Collection.objects.all())
    # # collection = serializers.StringRelatedField()
    # # collection =  CollectionSerializer()
    # collection =serializers.HyperlinkedRelatedField(queryset = Collection.objects.all(),view_name='collection-detail')

    def calculate_tax(self,product:Product):
        return  product.unit_price * Decimal(1.1)
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model =Review
        fields = ['id','name','description','date',]

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id = product_id,**validated_data)
    

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product =SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cartItem : CartItem):
        return cartItem.quantity * cartItem.product.unit_price
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only = True)
    items = CartItemSerializer(many =True, read_only = True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self,cart:Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    class Meta:
        model = Cart
        fields = ['id','items','total_price']


class AddCartItemSerialazer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self,value):
        if not Product.objects.filter(pk = value).exists():
            raise serializers.ValidationError('no Product with the given id was found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cartItem = CartItem.objects.get(cart_id=cart_id,product_id = product_id)
            cartItem.quantity += quantity
            cartItem.save()
            self.instance = cartItem
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id = cart_id,**self.validated_data)
        return self.instance
    
    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']


class UpdatedCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only =True)
    class Meta:
        model = Customer
        fields = ['id','user_id','birth_date','membership','phone']

class OrderItemSerialier(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id','product','unit_price','quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerialier(many = True)
    class Meta:
        model =Order
        fields = ['id','customer','placed_at','payment_status','items']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model =Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self,cart_id):
        if not Cart.objects.filter(pk =cart_id ).exists():
            raise serializers.ValidationError('no cart with the given id was found')
        if CartItem.objects.filter(cart_id = cart_id ).count() == 0:
            raise serializers.ValidationError('the cart is empty')
        return cart_id

    def save(self, **kwargs):
        # print(self.validated_data['cart_id'])
        # print(self.context['user_id'])
        with transaction.atomic():

            customer = Customer.objects.get(user_id = self.context['user_id'])
            order = Order.objects.create(customer = customer)

            cartItems = CartItem.objects.select_related('product').filter(cart_id = self.validated_data['cart_id'])

            orderItems =  [OrderItem(
                            order = order,
                            product = item.product,
                            unit_price = item.product.unit_price,
                            quantity = item.quantity,

                        ) for item in cartItems
            ]

            OrderItem.objects.bulk_create(orderItems)
            Cart.objects.filter(pk = self.validated_data['cart_id']).delete()

            order_created.send_robust(self.__class__,order = order)
            return order


