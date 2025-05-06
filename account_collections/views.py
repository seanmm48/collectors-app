#object or 404 gets object with given form or raises 404 error
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Collection, Item
from .forms import CollectionForm, ItemForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Sum
import json
from django.core.serializers.json import DjangoJSONEncoder

# Defining views to render corresponding HTML files
def homepage(request):
    return render(request, "HTML_Homepage.html")

def user_login(request):
    if request.method == "POST":
        # Get username and password from the form
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            django_login(request, user)
            return redirect('userHomepage')  # Redirect to userHomepage after successful login
        else:
            #messages.error(request, "Invalid username or password")  # Show error message
            #return redirect('login')  # Redirect back to the login page
            return render(request, "HTML_Login.html", {"error": "Invalid username or password"})  # Show error message


    return render(request, "HTML_Login.html")

def logout_view(request):
    logout(request)
    return redirect('homepage')  # Redirect to homepage after logout

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Ensure it's an AJAX request
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        # Validate form inputs
        if not username or not email or not password or not confirm_password:
            error_msg = "All fields are required!"
            return JsonResponse({"success": False, "error": error_msg}, status=400) if is_ajax else render(request, "HTML_SignUp.html", {"error": error_msg})

        if password != confirm_password:
            error_msg = "Passwords do not match!"
            return JsonResponse({"success": False, "error": error_msg}, status=400) if is_ajax else render(request, "HTML_SignUp.html", {"error": error_msg})

        if User.objects.filter(username=username).exists():
            error_msg = "Username already exists!"
            return JsonResponse({"success": False, "error": error_msg}, status=400) if is_ajax else render(request, "HTML_SignUp.html", {"error": error_msg})

        if User.objects.filter(email=email).exists():
            error_msg = "Email already in use!"
            return JsonResponse({"success": False, "error": error_msg}, status=400) if is_ajax else render(request, "HTML_SignUp.html", {"error": error_msg})

        try:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            django_login(request, user)  # Log in the user immediately

            # Always return JSON if AJAX request, otherwise redirect
            if is_ajax:
                return JsonResponse({'success': True, 'redirect_url': '/login/'})
            return redirect("login")

        except Exception as e:
            error_msg = str(e)
            return JsonResponse({"success": False, "error": error_msg}, status=500) if is_ajax else render(request, "HTML_SignUp.html", {"error": error_msg})

    return render(request, "HTML_SignUp.html")  # Render page for GET request

#only authenticated users can access
@login_required
def userHomepage(request):

    # Fetch collections associated with the logged-in user
    collections = Collection.objects.filter(user=request.user)
    
    total_purchased_price = 0
    total_retail_price = 0
    total_items = 0

    #Iterating through each collection and its associated items
    for collection in collections:
        for item in collection.items.all():  # Make sure `items` is a related field
            total_purchased_price += item.purchased_price
            total_retail_price += item.retail_price
            total_items += 1  #add total_items for each item
        
    
    # Render the homepage template and pass the collections context
    return render(request, "userHomepage.html", {'collections': collections, 'total_purchased_price': total_purchased_price,
        'total_retail_price': total_retail_price,'total_items': total_items,})

@login_required
def create_collection(request):
    if request.method == 'POST':
        collection_form = CollectionForm(request.POST, prefix='collection')
        item_form = ItemForm(request.POST, request.FILES, prefix='item')

        if collection_form.is_valid() and item_form.is_valid():
            collection = collection_form.save(commit=False)
            collection.user = request.user
            collection.save()

            item = item_form.save(commit=False)
            item.collection = collection
            item.save()

            return redirect('collection_detail', collection_id=collection.id)

        # If not valid, fall through to re-render the page below
    else:
        collection_form = CollectionForm(prefix='collection')
        item_form = ItemForm(prefix='item')

    return render(request, 'create_collection.html', {
        'collection_form': collection_form,
        'item_form': item_form,
    })

#CREATE collection_detail view
#Example
def collection_detail(request, collection_id):
    # Retrieve the collection using the ID
    collection = get_object_or_404(Collection, id=collection_id)

    # Fetch all items associated with this collection
    items = collection.items.all()

    # Initialize total prices and lists for purchase dates and prices
    total_purchased_price = 0
    total_retail_price = 0
    total_items = len(items)

    # Prepare data for the charts (Purchase vs. Retail Price Over Time)
    purchase_dates = []
    purchase_prices = []
    retail_prices = []

    for item in items:
        total_purchased_price += item.purchased_price
        total_retail_price += item.retail_price
        purchase_dates.append(item.date_purchased)
        purchase_prices.append(item.purchased_price)
        retail_prices.append(item.retail_price)

    # Serialize purchase dates into a JSON-compatible format (ISO 8601)
    purchase_dates_serialized = json.dumps([date.isoformat() for date in purchase_dates], cls=DjangoJSONEncoder)

    return render(request, 'collection_detail.html', {
        'collection': collection,
        'items': items,
        'total_purchased_price': total_purchased_price,
        'total_retail_price': total_retail_price,
        'total_items': total_items,
        'purchase_dates': purchase_dates_serialized,  # serialize dates to JSON
        'purchase_prices': json.dumps(purchase_prices, cls=DjangoJSONEncoder),  # serialize prices
        'retail_prices': json.dumps(retail_prices, cls=DjangoJSONEncoder),  # serialize retail prices
    })

def add_item(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.collection = collection  # Set the collection for the item
            item.save()
            return redirect('collection_detail', collection_id=collection.id)  # Redirect to the collection detail page
    else:
        form = ItemForm()

    #return render(request, 'add_item.html', {'form': form, 'collection': collection})
    return render(request, 'item_form.html', {
        'form': form,
        'collection': collection,
        'is_edit': False
    })

@login_required
def delete_collection(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    if request.method == 'POST':
        collection.delete()
        return redirect('userHomepage')  
    return redirect('collection_detail', collection_id=collection_id)

@login_required
def edit_item(request, collection_id, item_id):
    collection = get_object_or_404(Collection, id=collection_id)
    item = get_object_or_404(Item, pk=item_id, collection=collection)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_detail', collection_id=collection.id, item_id=item.id)
    else:
        form = ItemForm(instance=item)

    return render(request, 'item_form.html', {
        'form': form,
        'collection': collection,
        'item': item,
        'is_edit': True
    })

@login_required
def delete_item(request, collection_id, item_id):
    item = get_object_or_404(Item, pk=item_id, collection_id=collection_id)

    if request.method == 'POST':
        item.delete()
        return HttpResponseRedirect(reverse('collection_detail', args=[collection_id]))

    return render(request, 'delete_item.html', {'item': item})

@login_required
def item_detail(request, collection_id, item_id):
    collection = get_object_or_404(Collection, id=collection_id)
    item = get_object_or_404(Item, id=item_id, collection=collection)
    return render(request, 'item_detail.html', {'collection': collection, 'item': item})
