from typing import Any, List, Optional, Tuple
from django.contrib import admin ,messages
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse 
from django.utils.html import format_html, urlencode


from tags.models import TagItem
# from django.db.models.query import QuerySet
# from django.http.request import HttpRequest
from . import models
# Register your models here.


class InventoryFilter(admin.SimpleListFilter):
    title = 'By Inventory'
    parameter_name ='inventory_filter'

    def lookups(self, request, model_admin):
        return [
            ('<10','Low')
        ]
    
    def queryset(self, request, queryset: QuerySet) :
        if self.value() =='<10':
            return queryset.filter(inventory__lt=10)

# Product model......
# ......



@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields =['title']
    autocomplete_fields =['collection']
    prepopulated_fields ={
        'slug':['title']
    }
    actions = ['clear_inventory']
   
    list_display = ['title','unit_price','inventory_status','collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related =['collection']
    list_filter  =['collection','last_update',InventoryFilter]
    
    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'
    
    
    def collection_title(self,product):
        return product.collection.title

    @admin.action(description='Clear Inventory')
    def clear_inventory(self,request,queryset:QuerySet):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} Products were Successfuly Updated',
            messages.ERROR,
        )

# customer model............................
# ..........................................
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    
    list_display = ['first_name','last_name','membership','orders_count']
    list_editable = ['membership']
    list_per_page =10
    ordering = ['first_name','last_name']
    search_fields = ['first_name__istartswith','last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders_count(self,customer):
        url =(reverse('admin:store_order_changelist')
              +'?'
              +urlencode({
                  'customer__id':str(customer.id)
              }))
        return format_html('<a href="{}">{}</a>' ,url,customer.orders_count)
        

    def get_queryset(self, request) :
        return super().get_queryset(request).annotate(orders_count =Count('order'))

# order model....................................
# ...............................................
class OrderItemInline(admin.TabularInline):
    autocomplete_fields =['product']
    model = models.OrderItem
    min_num = 1
    max_num = 10
    extra =0

@admin.register(models.Order)
class OrderAmin(admin.ModelAdmin):
    inlines =[OrderItemInline]
    autocomplete_fields =['customer']
    list_display =['id','placed_at','customer']

# collection model ..........................................
# ...........................................................
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields=['title']
    list_display = ['title','products_count']

    @admin.display(ordering='products_count')
    def products_count(self,collection):
        url = (reverse('admin:store_product_changelist') 
               +'?'
               + urlencode({
                   'collection__id':str(collection.id)
               }))
        return format_html('<a href="{}">{}</a>',url,collection.products_count)
        
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count = Count('products'))