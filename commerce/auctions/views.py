from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import *
from django import forms
from django.utils import timezone
import datetime

class NewListingForm(forms.Form):
    title = forms.CharField(
        max_length=64, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Title', 
            'autofocus': 'autofocus'
        })
    )
    description = forms.CharField(
        max_length=512,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'placeholder': 'Description'
        })
    )
    price = forms.DecimalField(
        min_value=1, 
        max_value=1000000,
        decimal_places=2, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Price', 
            'step': '0.01'
        })
    )
    auction_duration = forms.IntegerField(
        min_value=1, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Auction Duration (Hours)'
        })
    )
    image_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Image URL'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Category'
        }),
        empty_label="Select Category"
    )

def index(request):
    current_time = timezone.now()
    listings = Auction.objects.all()

    return render(request, "auctions/index.html", {
        "title": "Listings",
        "listings": listings,
        "current_time": current_time,
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def new_listing_view(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = NewListingForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                price = form.cleaned_data['price']
                auction_duration = form.cleaned_data['auction_duration']
                image_url = form.cleaned_data['image_url']
                category = form.cleaned_data['category']
                end_date = timezone.now() + timezone.timedelta(hours=auction_duration)

                auction = Auction.objects.create(
                    title=title,
                    description=description,
                    starting_bid=price,
                    current_bid=price,
                    owner=request.user,
                    end_date=end_date,
                    image_url=image_url,
                    category=category
                )
                return HttpResponseRedirect(reverse("index"))
        else:
            print("here3")
            form = NewListingForm()
            return render(request, "auctions/new-listing.html", {
                "form" : form,
            })
    else:
        return HttpResponseRedirect(reverse("login"))
    
def listing(request, listing_id):
    try:
        listing = Auction.objects.get(pk=listing_id)
    except Auction.DoesNotExist:
        return HttpResponse("Listing not found.", status=404)
    
    user_has_highest = False
    try:
        if listing.bids.latest('id').bidder == request.user:
            user_has_highest = True
    except:
        pass

    if request.user.is_authenticated and request.method == "POST":
        if request.POST.get("comment") == "true":
            comment_text = request.POST.get("text")
            comment = Comment.objects.create(
                commenter=request.user,
                listing=listing,
                comment=comment_text
            )
        else:
            bid_price = request.POST.get("price")
            if bid_price == "":
                bid_price = "0"
            if float(bid_price) > listing.current_bid:
                bid = Bid.objects.create(
                        bid=float(bid_price),
                        bidder=request.user,
                        listing=listing,
                    )
            else:
                return render(request, "auctions/listing.html", {
                    "message": "Bid is too low",
                    "watching": request.user.watching.filter(pk=listing_id).exists(),
                    "listing": listing,
                    "current_time": timezone.now(),
                    "user_has_highest": user_has_highest,
                    "comments": listing.comments.all(),
                })
    
    return render(request, "auctions/listing.html", {
        "watching": request.user.watching.filter(pk=listing_id).exists(),
        "listing": listing,
        "current_time": timezone.now(),
        "user_has_highest": user_has_highest,
        "comments": listing.comments.all(),
    })

def watchlist(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            listing_id = request.POST.get('listing_id')
            listing = get_object_or_404(Auction, id=listing_id)
            if request.POST.get('remove') == "true":
                request.user.watching.remove(listing)
            else:
                request.user.watching.add(listing)
        current_time = timezone.now()
        listings = request.user.watching.all()

        return render(request, "auctions/index.html", {
            "title":"Watchlist",
            "listings": listings,
            "current_time": current_time,
        })
    else:
        return HttpResponseRedirect(reverse(login))
    
def category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return HttpResponse("Category not found.", status=404)

    current_time = timezone.now()
    listings = category.auctions.all()

    return render(request, "auctions/index.html", {
        "title": f"Category: {category.name}",
        "listings": listings,
        "current_time": current_time,
    })

    
def category_finder(request):
    return render(request, "auctions/category.html", {
        "categories": Category.objects.all(),
    })