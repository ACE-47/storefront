from django.shortcuts import render
from django.db.models import Q,F,Value,Func
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Concat
from store.models import Product,OrderItem,Order,Customer
from tags.models import TagItem

# Create your views here.
def hello(request):
    # query_set = Product.objects.filter(inventory=F('unit_price'))
    # query_set = Product.objects.order_by('unit_price','-title')[:8]
    # query_set =Product.objects.filter(id__in = OrderItem.objects.values('product_id').distinct()).order_by('title')
    # query_set =Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    # query_set = Customer.objects.annotate(
    #     full_name =Func(F('first_name'),Value(''),F('last_name'),function='CONCAT')
    # )
    # query_set = Customer.objects.annotate(
    #     full_name =Concat('first_name',Value(''),'last_name')
    # )
    query_set = TagItem.objects.get_tags_for(Product,1)
    

    return render(request,'hello.html',{
        'name':'Haider',
        'orders': query_set
    })