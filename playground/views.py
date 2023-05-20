

from django.core.mail import BadHeaderError
from templated_mail.mail import BaseEmailMessage
from django.shortcuts import render
from .tasks import notify_customers


# Create your views here.
def hello(request):
    # try:
    #     message = BaseEmailMessage(template_name= 'emails/hello.html',
    #                                context = {'name' : 'ace47',})
        
    #     message.send(['haider@test.com'])
    # except BadHeaderError:
    #     pass

    notify_customers.delay('Hello World')
    return render(request,'hello.html',{
        'name':'Haider',
    })