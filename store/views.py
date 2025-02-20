from django.shortcuts import render,get_object_or_404
from rest_framework import permissions 
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.generics import ListCreateAPIView ,RetrieveUpdateDestroyAPIView
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

from django.db.models.aggregates import Count

from .filters import ProductFilter
from .models import Cart, CartItem, Customer, Order, OrderItem, Product,Collection, ProductImage,Review
from .serializers import AddCartItemSerialazer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer ,CollectionSerializer,ReviewSerializer, UpdateOrderSerializer, UpdatedCartItemSerializer
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission
# Create your views here.


# class ProductList(APIView):
#     def get(self,request):
#         prodcuts =Product.objects.all()
#         serializer = ProductSerializer(prodcuts,many =True,context={'request': request})
#         return Response(serializer.data)
    
#     def post(self,request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data,status=status.HTTP_201_CREATED)

# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_serializer_context(self):
#         return {'request':self.request}
        
# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset =Product.objects.all()
#     serializer_class =ProductSerializer

#     def delete(self,request,pk):
#         product = get_object_or_404(Product,pk=pk)
#         if product.orderitem_set.count() > 0:
#             return Response ({'error':'Product cannot deleted becaust it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class ProductViewSet(ModelViewSet):
    queryset =Product.objects.prefetch_related('images').all()
    serializer_class =ProductSerializer
    filter_backends =[DjangoFilterBackend,SearchFilter,OrderingFilter]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']

    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     print(collection_id)
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id = collection_id)
       
    #     return queryset

    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id = kwargs['pk']).count > 0 :
            return Response ({'error':'Product cannot deleted becaust it is associated with an order item'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
       
# class CollectionList(ListCreateAPIView):
#     queryset =  Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializer


# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset =Collection.objects.annotate(products_count = Count('products'))
#     serializer_class = CollectionSerializer

#     def delete(self, request, pk):
#         collection = get_object_or_404(
#         Collection.objects.annotate(
#         products_count=Count('products')), pk=pk)
#         if collection.products.count() > 0:
#             return Response({'error':'Collection cannot deleted becaust it is conains Prodcut Items'},status=status.HTTP_405_METHOD_NOT_ALLOWED,)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionsViewSet(ModelViewSet):
    queryset =  Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes =[IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    # serializer_class =CartItemSerializer
    http_method_names =['get','patch','post','delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerialazer
        elif self.request.method == 'PATCH':
            return UpdatedCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id' : self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id = self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(ModelViewSet):
    
    queryset =Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes =[IsAdminUser]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     else:
    #         return [IsAuthenticated()]

    @action(detail=True,permission_classes=[ViewCustomerHistoryPermission])
    def history(self,request,pk):
        return Response('ok')

    @action(detail=False,methods=['GET','PUT'],permission_classes =[IsAdminOrReadOnly])
    def me(self,request):
        customer =  Customer.objects.get(user_id = request.user.id) # here the get_or_create method return a tuple which contain the customer object and the boolean which refere if its created or not 
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer,data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete','head','options']

    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    # queryset = Order.objects.all()
    # serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,context = {'user_id':self.request.user.id })
        serializer.is_valid(raise_exception= True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    # def get_serializer_context(self):
    #     return 

    def get_queryset(self):
        user =self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id= Customer.objects.only('id').get(user_id = user.id )
        return Order.objects.filter(customer_id = customer_id)
    


class ProductImageViewSet(ModelViewSet):

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id = self.kwargs['product_pk'])

    serializer_class = ProductImageSerializer