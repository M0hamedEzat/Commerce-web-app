from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, AuctionListing, Bid, Comment
from django import forms


class ListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'starting_bid', 'image_url']

class BidingForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

def index(request):
    listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        'listings' : listings
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


def create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            list = form.save(commit=False)
            list.owner = request.user
            list.save()
            return redirect('index')

    return render(request, "auctions/create.html", {
        'form': ListingForm
    })


def listing_details(request, listing_id):
    try:
        item = AuctionListing.objects.get(id=listing_id)
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'place_bid':
                form = BidingForm(request.POST)
                if form.is_valid():
                    bid = form.save(commit=False)
                    bid.listing = item
                    bid.user = request.user
                    if not item.is_active:
                        return render(request, "auctions/list.html",{
                            'error' : "Item is closed",
                            'item' : item,
                            'form' : BidingForm(),
                            'comment_form' : CommentForm(),
                        })
                    elif (bid.listing.current_price or bid.listing.starting_bid) > bid.amount:
                        return render(request, "auctions/list.html",{
                            'error' : "Bid is too low",
                            'item' : item,
                            'form' : BidingForm(),
                            'comment_form' : CommentForm(),

                        })
                    elif bid.user == item.owner:
                        return render(request, "auctions/list.html",{
                            'error' : "You CAN'T bid for Your own Item",
                            'item' : item,
                            'form' : BidingForm(),
                            'comment_form' : CommentForm(),
                        })
                    else:
                        bid.save()
                        item.current_price = bid.amount
                        item.save()
                        return redirect('listing_details', listing_id)
            elif action == 'place_comment':
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                    comment = comment_form.save(commit=False)
                    comment.listing = item
                    comment.user = request.user
                    comment.save()
                    return redirect('listing_details', listing_id)
                else:
                    return render(request, "auctions/list.html", {
                        'item': item,
                        'form': form,
                        'comment_form' : CommentForm(),
                    })
        else:
            form = BidingForm()
        return render(request, "auctions/list.html", {
            'item': item,
            'form': form,
            'comment_form' : CommentForm(),
        })
    except AuctionListing.DoesNotExist:
        return redirect('index')  # Handle case where listing doesn't exist
    

def watchlist(request, item_id):
    item = AuctionListing.objects.get(pk=item_id)
    if item in request.user.watchlist.all():
        request.user.watchlist.remove(item)
    else:
        request.user.watchlist.add(item)
    return redirect('listing_details', listing_id=item_id)


def close(request, item_id):
    item = AuctionListing.objects.get(pk=item_id)
    if item.owner == request.user:
        item.is_active = False
        highest_bid = item.bids.order_by('-amount').first()
        if highest_bid:
            item.winner = highest_bid.user
        item.save()

    return redirect('listing_details', item_id)

def mywatchlist(request):
    watchlist = request.user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        'watchlist' : watchlist
    })


