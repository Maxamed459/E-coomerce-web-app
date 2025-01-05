from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comment,Bid

def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    # knowing the type of product by using listingData Foriengkey
    cat_spec = listingData.category
    if cat_spec.CategoryName == "Laptops":
        listingName = "Laptop"
    elif cat_spec.CategoryName == "Mobiles":
        listingName = "Mobile"
    else:
        listingName = "Accessories"
    islistingInWatchlist = request.user in listingData.wachlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData, 
        "ListingName":listingName,
        "islistingInwachlist": islistingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })

def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    islistingInWatchlist = request.user in listingData.wachlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html", {
        "listing": listingData, 
        "islistingInwachlist": islistingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "Congratulation! your auction is closed"
    })


def displayWachlist(request):
    currentUser = request.user
    listings = currentUser.Listingwachlist.all()
    return render(request, "auctions/watchlist.html", {
        "Listings": listings
    })


def removeWachlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user 
    listingData.wachlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addWachlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.wachlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    allcategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "Listings": activeListings,
        "categories": allcategories
    })

def addBid(request, id):
    newbid = request.POST['newBid']
    listingData = Listing.objects.get(pk=id)
    islistingInWatchlist = request.user in listingData.wachlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    cat_spec = listingData.category
    if cat_spec.CategoryName == "Laptops":
        listingName = "Laptop"
    elif cat_spec.CategoryName == "Mobiles":
        listingName = "Mobile"
    else:
        listingName = "Accessories"
    if int(newbid) > listingData.price.bid:
        updateBid = Bid(user=request.user, bid=int(newbid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid was updated successfully",
            "update": True,
            "islistingInwachlist": islistingInWatchlist,
            "allComments": allComments,
            "ListingName":listingName,
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid update Failed",
            "update": False,
            "islistingInwachlist": islistingInWatchlist,
            "allComments": allComments,
            "ListingName":listingName,
        })

def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST['newComment']

    newComment = Comment (
        author=currentUser,
        listing=listingData,
        comment=message
    )

    newComment.save()
    
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def displayCategory(request):
    if request.method == "POST":
        categoryFromform = request.POST['category']
        category = Category.objects.get(CategoryName=categoryFromform)
        activeListings = Listing.objects.filter(isActive=True, category=category)
        allcategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "Listings": activeListings,
            "categories": allcategories
        })


def createListing(request):
    if request.method == "GET":
        allcategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allcategories
        }) 
    
    else:
        # get the data from the form 
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageUrl"]
        price = request.POST["price"]
        category = request.POST["category"]

        # who is the user
        currentUser = request.user

        # get all content about the particular category
        categoryData = Category.objects.get(CategoryName=category)

        #create a bid object
        bid =Bid(bid=int(price), user=currentUser)
        bid.save()
        # Create a new listing object
        newListing = Listing(
            title = title,
            description = description, 
            imageUrl = imageUrl, 
            price = bid, 
            category = categoryData, 
            owner = currentUser
        )

        # Inset the object in our database
        newListing.save()
        
        # Redirect to index page
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
