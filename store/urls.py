from django.urls import path
# from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router =routers.DefaultRouter()

router.register('products',views.ProductViewSet,basename='products')
router.register('collections',views.CollectionsViewSet)
router.register('carts',views.CartViewSet)
router.register('customers',views.CustomerViewSet)
router.register('orders',views.OrderViewSet,basename='orders')

products_router = routers.NestedDefaultRouter(router,'products',lookup='product')
products_router.register('reviews',viewset=views.ReviewViewSet, basename='product-reviews')
products_router.register('images',viewset=views.ProductImageViewSet, basename='product-images')


carts_router =  routers.NestedDefaultRouter(router,'carts',lookup='cart')
carts_router.register('items',viewset=views.CartItemViewSet,basename='cart-items')


urlpatterns = router.urls + products_router.urls + carts_router.urls

# urlpatterns = [
#     path('products/',views.ProductList.as_view()),
#     path('products/<int:pk>',views.ProductDetail.as_view()),
#     path('collections/',views.CollectionList.as_view()),
#     path('collections/<int:pk>',views.CollectionDetail.as_view(),name='collection-detail'),

# ]