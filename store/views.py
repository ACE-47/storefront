from django.shortcuts import render,get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView ,RetrieveUpdateDestroyAPIView
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter

from django.db.models.aggregates import Count

from .filters import ProductFilter
from .models import OrderItem, Product,Collection,Review
from .serializers import ProductSerializer ,CollectionSerializer,ReviewSerializer
from .pagination import DefaultPagination
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
    queryset =Product.objects.all()
    serializer_class =ProductSerializer
    filter_backends =[DjangoFilterBackend,SearchFilter,OrderingFilter]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilter
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']
    pagination_class = DefaultPagination

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
