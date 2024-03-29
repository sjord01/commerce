from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing


def index(request):
    active_listings = Listing.objects.filter(is_active = True)
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })

def create_listing(request):
    if request.method == "GET":
        all_categories = Category.objects.all().order_by('category')
        return render(request, "auctions/create.html", {
            "categories": all_categories
        })
    
    #Meaning, not "GET" but "POST"
    else:

        #Get the data from form
        title           = request.POST["title"]
        description     = request.POST["description"]
        image_url       = request.POST["image_url"]
        price           = request.POST["price"]
        category        = request.POST["category"]

        #Verify the user
        current_user = request.user

        #Get all content about the particular category
        category_data = Category.objects.get(category_name = category)

        #Create new listing object
        new_listing = Listing(
            title           = title,
            description     = description,
            image_url       = image_url,
            price           = float(price),
            category        = category_data,
            owner           = current_user,

        )

        #Insert new listing object into django database
        new_listing.save()

        #redirect into index page
        return HttpResponseRedirect(reverse(index))


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
