from django.shortcuts import render,redirect
from .models import *
import json
import datetime
from .utils import cookieCart,cartData,guestOrder
from .forms import UserRegistrationForm,ReviewForm,CustomReviewForm
from django.contrib import messages
from .filters import ProductFilter
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth.decorators import login_required
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.shortcuts import render
from .apps import StoreConfig
from django.http import JsonResponse
from rest_framework.views import APIView


class call_model(APIView):
    def get(self, request,pk):
        if request.method == 'GET':
            cur_product=Product.objects.get(id=pk)
            sound = request.GET.get('sound')
            lis=[]
            lis.append(sound)
            prediction = StoreConfig.classifier.predict(lis)
            r=int(prediction[0])
            rate=request.GET.get('rating_given')
            r=(r+float(rate))
            r=r/2
            Review.objects.create(
                user=request.user,
                product=cur_product,
                rating=r,
                review=sound,
            )
            print('Prediction:',prediction)
            return redirect('store')


def see_rating(request,pk):
    cur_product=Product.objects.get(id=pk)
    all_reviews=Review.objects.all()
    i=1
    r=0
    lis=[]
    for review in all_reviews:
        if cur_product==review.product:
            lis.append(review.review)
            r=r+review.rating
            i=i+1

    r=r/i

    return render(request,'store/see_rating.html',{'rating':r,'product':cur_product,'reviews':lis})

def createReview(request,pk):
    if request.method=='POST':
        form=CustomReviewForm(request.POST)
        cur_product=Product.objects.get(id=pk)
        if form.is_valid():
            Review.objects.create(
                user=request.user,
                product=cur_product,
                rating=form.cleaned_data.get('rating'),
            )
            return redirect('store')
    else:
        form=ReviewForm()
    cur_product=Product.objects.get(id=pk)
    return render(request,'store/review_create.html',{'form':form,'product_id':cur_product.pk,'product':cur_product})

temp={}
def store(request):

    if request.user.is_authenticated:
        createCustomer=Customer.objects.get_or_create(user=request.user,name=request.user.username,email=request.user.email)
        current_users_name=request.user.username
        print(current_users_name)

        # new_cust=Customer(user=request.user,name=request.user.username,)
        # new_cust.save()

    data = cartData(request)

    cartItems = data['cartItems']

    products=Product.objects.all()

    


    myFilter = ProductFilter(request.GET,queryset=products)
    products = myFilter.qs

    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context={'products':products,'cartItems':cartItems,'myFilter':myFilter}
    return render(request,'store/store.html',context)

def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    temp['items']=items
    temp['order']=order
    temp['cartItems']=cartItems
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/cart.html',context)

def checkout(request):
    data=cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order,'cartItems':cartItems}
    return render(request,'store/checkout.html',context)

def updateitem(request):
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']
    print('ProductId:',productId)
    print('Action:',action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()


    return JsonResponse('Item was added',safe=False)


def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)



    else:
        customer,order=guestOrder(request,data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )


    return JsonResponse('Payment Complete..',safe=False)


def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            u = form.cleaned_data.get('username')
            v = form.cleaned_data.get('email')
            form.save()
            messages.success(request,f'Account Created successfully for {u}')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request,'store/register.html',{'form':form})

data={}

@login_required(login_url='login')
def previousOrders(request):
    cur_user=request.user
    cur_cust=Customer.objects.filter(user=cur_user).first()
    cur_cust_orders=Order.objects.filter(customer=cur_cust)

    all_order_details=[]

    for order in cur_cust_orders:
        all_order_items=OrderItem.objects.filter(order=order)
        all_product_details=[]
        for orderItem in all_order_items:
            temp={'product_name':orderItem.product.name,
                  'product_image':orderItem.product.image,
                  'product_price':orderItem.product.price,
                  'product_id':orderItem.product.id,
                  'product_quantity':orderItem.quantity}
            all_product_details.append(temp)
        qwe={'order':order,'details':all_product_details}
        all_order_details.append(qwe)


    data['all_order_details']=all_order_details
    context={
        'all_order_details':all_order_details,
    }
    return render(request,'store/my_orders.html',context)



def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

class ViewPDF(View):
	def get(self, request, *args, **kwargs):
		pdf = render_to_pdf('store/pdf_template.html', data)
		return HttpResponse(pdf, content_type='application/pdf')



class ViewCurPDF(View):
	def get(self, request, *args, **kwargs):
		pdf = render_to_pdf('store/cur_pdf_template.html', temp)
		return HttpResponse(pdf, content_type='application/pdf')




def eachProductReview(request,pk):
    cur_product=Product.objects.get(id=pk)
    form=ReviewForm()
    return render(request,'store/each_product_review.html',{'product':cur_product,'form':form})





