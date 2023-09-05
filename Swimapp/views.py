import datetime
import os

import ipinfo
import requests
import stripe
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from geopy.distance import geodesic
from rest_framework import generics
from rest_framework.parsers import MultiPartParser
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from .forms import *
from .serialiser import *


# Create your views here.

def register(request):
    current_year = datetime.datetime.now().year
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)

            return render(request, 'Swimapp/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    context = {
        'user_form': user_form,
        'year': current_year,
    }
    return render(request, 'Swimapp/register.html', context)


@login_required
def edit(request):
    current_year = datetime.datetime.now().year
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'year': current_year
    }
    return render(request, 'Swimapp/edit.html', context)


def user_login(request):
    current_year = datetime.datetime.now().year

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = form.user  # Use the authenticated user from the form

            if user.is_active:
                login(request, user)
                return redirect('mysite:homepage')
            else:
                messages.error(request, 'Your account is disabled. Please contact support.')

    else:
        form = LoginForm(request)

    context = {
        'form': form,
        'year': current_year
    }
    return render(request, 'registration/login.html', context)


def homepage(request):
    current_year = datetime.datetime.now().year
    ipinfo_token = '4a8c2d33243761'

    # Get IP information
    ip_data = None
    if ipinfo_token:
        ip_handler = ipinfo.getHandler(access_token=ipinfo_token)
        ip_data = ip_handler.getDetails()

    user_lat = None
    user_long = None
    if ip_data:
        user_lat = ip_data.latitude
        user_long = ip_data.longitude

    swimming_spots = SwimmingSpot.objects.all()

    def filter_swim_spot(spots, user_coords, max_distance_miles=70):
        nearby_spots = []
        for spot in spots:
            distance = geodesic(user_coords, (spot.latitude, spot.longitude)).miles
            if distance <= max_distance_miles:
                nearby_spots.append(spot)

        # Order nearby_spots by highest average_rating
        nearby_spots = sorted(nearby_spots, key=lambda spot: spot.average_rating, reverse=True)

        return nearby_spots

    nearby_swimming_spots = filter_swim_spot(swimming_spots, (user_lat, user_long))

    context = {
        'ip_data': ip_data,
        'nearby_swimming_spots': nearby_swimming_spots,
        'spots': swimming_spots,
        'year': current_year
    }
    return render(request, 'Swimapp/homepage.html', context)


def search_results(request):
    query = request.GET.get('query')

    if query:
        # Combine queries for city, spot name, and category using OR operator
        results = SwimmingSpot.objects.filter(
            # Q(city__icontains=query) |
            Q(title__icontains=query) |
            Q(category__name__icontains=query)
        )
    else:
        results = SwimmingSpot.objects.all()

    context = {'results': results}
    return render(request, 'Swimapp/search_results.html', context)


def explore(request):
    current_year = datetime.datetime.now().year
    # mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
    mapbox_access_token = 'pk.eyJ1IjoiYmx1ZXRocml2ZSIsImEiOiJjbGtnMW10cWMxNnhuM2RxanNsYTd2NjF3In0.SUoV3MhMLlzub7yMGxXFIw'
    # Get the 'category' and 'user_id' query parameters from the request
    category_id = request.GET.get('category')
    user_id = request.GET.get('user_id')

    # Retrieve all spots initially
    all_spots = SwimmingSpot.objects.all()

    # Apply filtering based on category if category_id is provided
    if category_id:
        filtered_spots = all_spots.filter(category_id=category_id)
    else:
        filtered_spots = all_spots

    user_spots = filtered_spots

    if user_id:
        if user_id == str(request.user.id):
            user_spots = filtered_spots.filter(user_id=request.user.id)
        else:
            return redirect('/explore')

    categories = Category.objects.all()

    context = {
        'mapbox_access_token': mapbox_access_token,
        'spots': user_spots,
        'categories': categories,
        'year': current_year,
    }
    return render(request, 'Swimapp/explore.html', context)


def spot_detail(request, spot):
    # mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
    mapbox_access_token = 'pk.eyJ1IjoiYmx1ZXRocml2ZSIsImEiOiJjbGtnMW10cWMxNnhuM2RxanNsYTd2NjF3In0.SUoV3MhMLlzub7yMGxXFIw'
    current_year = datetime.datetime.now().year
    spot = get_object_or_404(SwimmingSpot, slug=spot)
    comments = Comment.objects.filter(swimming_spot=spot)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)

        if 'rating' in request.POST and comment_form.is_valid():
            selected_rating = int(request.POST.get('rating'))
            Rating.objects.create(
                user=request.user,
                swimming_spot=spot,
                rating=selected_rating
            )
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.swimming_spot = spot
            comment.save()

            FeedItem.objects.create(user=request.user, content_object=comment)

            # Clear the form data after successful submission
            comment_form = CommentForm()

    else:
        comment_form = CommentForm()

    context = {
        'mapbox_access_token': mapbox_access_token,
        'spot': spot,
        'comments': comments,
        'comment_form': comment_form,
        'year': current_year
    }
    return render(request, 'Swimapp/spot.html', context)


def edit_swimming_spot(request, spot_id):
    swimming_spot = SwimmingSpot.objects.get(pk=spot_id)

    if request.method == 'POST':
        form = SwimmingSpotForm(request.POST, request.FILES, instance=swimming_spot)

        if form.is_valid():
            form.save()
            # Handle the uploaded files here
            for uploaded_file in form.cleaned_data['images']:
                Image.objects.create(swimming_spot=swimming_spot, image=uploaded_file)

            return redirect('/explore')
    else:
        form = SwimmingSpotForm(instance=swimming_spot)

    return render(request, 'Swimapp/edit_swimming_spot.html', {'form': form})


@login_required
def delete_spot(request, spot_id):
    spot = get_object_or_404(SwimmingSpot, id=spot_id, user=request.user)

    if request.method == 'POST':
        spot.delete()
        return redirect('mysite:explore')  # Redirect to explore page after deletion

    context = {
        'spot': spot
    }
    return render(request, 'Swimapp/confirm_delete.html', context)


@login_required
def my_spots(request):
    spots = SwimmingSpot.objects.filter(user=request.user)

    context = {
        'spots': spots,
    }
    return render(request, 'Swimapp/my_spots.html', context)


@login_required
def community(request):
    feed_items = FeedItem.objects.order_by('-created')[:100]  # You might want to limit or filter the items
    return render(request, 'Swimapp/community.html', {'feed_items': feed_items})


def about(request):
    return render(request, 'Swimapp/about.html')


class SwimmingSpotListView(generics.ListCreateAPIView):
    queryset = SwimmingSpot.objects.all()
    serializer_class = SwimmingSpotSerializer
    parser_classes = (MultiPartParser,)


SENDINBLUE_API_KEY = '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'


def subscribe_newsletter(request):
    form = SubscriberForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        # Send the email using SendinBlue
        api_key = SENDINBLUE_API_KEY
        sender_email = 'contact@swimspotter.com'
        recipient_email = email

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = api_key

        api_create = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
        create_contact = sib_api_v3_sdk.CreateContact(email=recipient_email, list_ids=[2])
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = "from the SwimSpotters!"
        sender = {"name": "SwimSpotters", "email": "contact@swimspotter.com"}
        reply_to = {"name": "SwimSpotters", "email": "contact@swimspotter.com"}
        html_content = "<html><body><h1>This is my first transactional email </h1></body></html>"
        to = [{"email": recipient_email, }]
        params = {"parameter": "My param value", "subject": "New Subject"}
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, reply_to=reply_to, html_content=html_content,
                                                       sender=sender, subject=subject)

        try:
            api_response_create_contact = api_create.create_contact(create_contact)
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(f"API Response Contact: {api_response_create_contact} ")
        except ApiException as e:
            print("Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % e)

        return HttpResponseRedirect('/')  # Redirect to a success page or the homepage

    return render(request, 'your_template.html', {'form': form})


def footer_newsletter_form():
    form = SubscriberForm()
    return {'footer_newsletter_form': form}


def redirect_to_home(request):
    return redirect('/')


@login_required
def list_plans(request):
    plans = Plan.objects.all()
    return render(request, 'Swimapp/subscription_plans.html', {'plans': plans})


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def subscribe(request, plan_id):
    plan = Plan.objects.get(pk=plan_id)
    stripe_publishable = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        # Check if the user has a Stripe customer ID
        if not request.user.profile.stripe_customer_id:
            # If the user doesn't have a Stripe customer ID, create one
            customer = stripe.Customer.create(email=request.user.email)
            request.user.profile.stripe_customer_id = customer.id
            request.user.profile.save()

        # Stripe checkout session data
        session_data = {
            'payment_method_types': ['card'],
            'mode': 'subscription',
            'client_reference_id': request.user.profile.stripe_customer_id,
            'line_items': [
                {
                    'price': plan.stripe_plan_id,  # Replace with the actual Stripe Price ID
                },
            ],
            'success_url': request.build_absolute_uri(reverse('Swimapp:completed')),
            'cancel_url': request.build_absolute_uri(reverse('Swimapp:canceled')),
        }

        # Create a Stripe checkout session
        session = stripe.checkout.Session.create(**session_data)

        # Redirect to Stripe Checkout page
        return redirect(session.url, code=303)
    else:
        context = {
            'plan': plan,
            'stripe_publishable': stripe_publishable,
        }

        return render(request, 'Swimapp/subscription_signup.html', context)
