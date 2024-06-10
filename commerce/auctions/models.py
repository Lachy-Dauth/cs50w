from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    watching = models.ManyToManyField("Auction", blank=True, related_name="watchers")


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    end_date = models.DateTimeField()
    image_url = models.URLField(max_length=200, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="auctions")

    def save(self, *args, **kwargs):
        if self.current_bid is None:
            self.current_bid = self.starting_bid
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")

    def save(self, *args, **kwargs):
        if self.bid <= self.listing.current_bid:
            raise ValueError("Bid must be higher than the current bid.")
        self.listing.current_bid = self.bid
        self.listing.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bidder.username} bids ${self.bid} on {self.listing.title}"


class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=512)

    def __str__(self):
        return f"{self.commenter.username}'s comment on {self.listing.title}"
