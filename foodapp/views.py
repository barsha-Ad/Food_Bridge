from django.shortcuts import render, redirect
from .models import FoodDonation
from .forms import FoodDonationForm
from .forms import HelpSupportForm
from .models import NGO
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User 
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from .serializers import FoodDonationSerializer
from .models import FoodDonation
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import random
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SignupSerializer
from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from .models import FoodDonation, Notification, UserProfile
from .models import FoodDonation, NGO, DonationRequest
from datetime import datetime
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .ai.recommendation import find_best_ngos

def donate_food(request):
    if request.method == "POST":
        form = FoodDonationForm(request.POST, request.FILES)
        if form.is_valid():
            donation = form.save()
            ngo_users = User.objects.filter(userprofile__role="NGO")
            for ngo in ngo_users:
                Notification.objects.create(
                    user=ngo,
                    message=f"New food donation from {donation.donor_name}"
                )
            return redirect("donation")
        else:
            print(form.errors)
    else:
        form = FoodDonationForm()
    return render(request, "donate_food.html", {"form": form})

def donation(request):
    donations = FoodDonation.objects.all().order_by('-id')
    return render(request, 'donation.html', {
        'donations': donations
    })

def help_support(request):
    if request.method == "POST":
        form = HelpSupportForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("help_support")
    else:
        form = HelpSupportForm()
    return render(request, "help_support.html", {"form": form})

def history(request):
    donations = FoodDonation.objects.all().order_by('-id')
    return render(request, 'history.html', {
        'donations': donations
    })
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    total = FoodDonation.objects.count()
    available = FoodDonation.objects.count()
    delivered = 0
    ngo = NGO.objects.count()
    category = FoodDonation.objects.values("category").annotate(total=Count("id"))
    recent = FoodDonation.objects.order_by("-id")[:5]
    context = {
        "total": total,
        "available": available,
        "delivered": delivered,
        "ngo": ngo,
        "category": category,
        "recent": recent,
    }
    return render(request, "dashboard.html", context)

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST['confirm_password']
        role = request.POST['role']
        if password != confirm:
            return render(request, "signup.html", {"error": "Passwords do not match"})
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists"})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        UserProfile.objects.create(
            user=user,
            role=role
        )
        return redirect('login')
    return render(request, "signup.html")

    
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user:
            auth_login(request, user)

            if user.userprofile.role == "DONOR":
                return redirect("dashboard")

            elif user.userprofile.role == "NGO":
                return redirect("ngo_dashboard")

        return render(request, "login.html", {
            "error": "Invalid Username or Password"
        })

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('login')

def ngo(request):
    ngos = NGO.objects.all()
    return render(request, "ngo.html", {"ngos": ngos})

def ngo_detail(request, ngo_id):

    ngo = get_object_or_404(
        NGO,
        id=ngo_id
    )

    return render(
        request,
        "ngo_detail.html",
        {
            "ngo": ngo
        }
    )

def home(request):
    return render(request,'home.html')

@login_required
def setting(request):

    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":

        password_form = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if password_form.is_valid():

            user = password_form.save()

            # User ko logout na kare
            update_session_auth_hash(request, user)

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect("setting")

    return render(
        request,
        "setting.html",
        {
            "password_form": password_form
        }
    )

def profile(request):
    return render(request,'profile.html')

def about(request):
    return render(request,'about.html')

@login_required
def ngo_dashboard(request):

    donations = FoodDonation.objects.all()
    search = request.GET.get("search", "")
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    city = request.GET.get("city", "")

    if search:
        donations = donations.filter(
            Q(food_name__icontains=search) |
            Q(donor_name__icontains=search) |
            Q(city__icontains=search)
        )

    if category:
        donations = donations.filter(category=category)

    if status:
        donations = donations.filter(status=status)

    if city:
        donations = donations.filter(city__icontains=city)

    context = {
        "donations": donations,

        "total_requests": FoodDonation.objects.count(),

        "accepted": FoodDonation.objects.filter(
            status="Accepted"
        ).count(),

        "pending": FoodDonation.objects.filter(
            status="Pending"
        ).count(),

        "rejected": FoodDonation.objects.filter(
            status="Rejected"
        ).count(),

        "completed": FoodDonation.objects.filter(
            status="Completed"
        ).count(),

        "search": search,
        "category": category,
        "status": status,
        "city": city,
    }

    return render(
        request,
        "ngo_dashboard.html",
        context
 )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_donation(request, donation_id):

    donation = get_object_or_404(FoodDonation, id=donation_id)

    donation.status = "Completed"
    donation.save()

    return Response(
        {"message": "Donation completed successfully"},
        status=status.HTTP_200_OK
    )

# @login_required
# def accept_donation(request, donation_id):

#     donation = get_object_or_404(
#         FoodDonation,
#         id=donation_id
#     )

#     donation.status = "Accepted"
#     donation.save()

#     # Send notification to donor
#     try:
#         donor = User.objects.filter(
#             email=donation.email
#         ).first()

#         if donor:
#             Notification.objects.create(
#                 user=donor,
#                 message=(
#                     f"Your food donation "
#                     f"'{donation.food_name}' has been accepted by an NGO."
#                 )
#             )

#     except Exception:
#         pass

#     return redirect("ngo_dashboard")

@login_required
def accept_donation(request, donation_id):

    donation = get_object_or_404(
        FoodDonation,
        id=donation_id
    )

    donation.status = "Accepted"
    donation.save()

    donor = User.objects.filter(
        email=donation.email
    ).first()

    print("DONATION EMAIL:", donation.email)
    print("DONOR FOUND:", donor)

    if donor:
        Notification.objects.create(
            user=donor,
            message=(
                f"Your food donation "
                f"'{donation.food_name}' has been accepted by an NGO."
            )
        )

    return redirect("ngo_dashboard")
@login_required
def complete_donation(request, donation_id):

    donation = get_object_or_404(
        FoodDonation,
        id=donation_id
    )

    # Change status
    donation.status = "Completed"
    donation.save()

    # Send notification to donor
    try:
        donor = User.objects.filter(
            email=donation.email
        ).first()

        if donor:
            Notification.objects.create(
                user=donor,
                message=(
                    f"Your food donation "
                    f"'{donation.food_name}' "
                    f"has been completed successfully."
                )
            )

    except Exception:
        pass

    return redirect("ngo_dashboard")

@login_required
def reject_donation(request, donation_id):

    donation = get_object_or_404(
        FoodDonation,
        id=donation_id
    )

    if request.method == "POST":

        reason = request.POST.get(
            "rejection_reason",
            ""
        ).strip()

        if not reason:
            return render(
                request,
                "reject_donation.html",
                {
                    "donation": donation,
                    "error": "Please enter a rejection reason."
                }
            )

        # Update donation status
        donation.status = "Rejected"
        donation.rejection_reason = reason
        donation.save()

        # Send notification to donor
        donor = User.objects.filter(
            email=donation.email
        ).first()

        if donor:
            Notification.objects.create(
                user=donor,
                message=(
                    f"Your food donation '{donation.food_name}' "
                    f"has been rejected. Reason: {reason}"
                )
            )

        return redirect("ngo_dashboard")

    return render(
        request,
        "reject_donation.html",
        {
            "donation": donation
        }
    )


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session["otp"] = str(otp)
            request.session["email"] = email
            send_mail(
                "Food Bridge Password Reset OTP",
                f"Your OTP is: {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return redirect("verify_otp")
        except User.DoesNotExist:
            return render(
                request,
                "forgot_password.html",
                {"error": "Email not registered."},
            )
    return render(request, "forgot_password.html")

def verify_otp(request):
    return render(request,'verify_otp.html')

def reset_password(request):
    return render(request,'reset_password.html')

def verify_otp(request):
    if request.method == "POST":

        entered_otp = request.POST.get("otp")
        saved_otp = request.session.get("otp")

        if entered_otp == saved_otp:
            return redirect("reset_password")
        else:
            return render(
                request,
                "verify_otp.html",
                {"error": "Invalid OTP"}
            )
    return render(request, "verify_otp.html")

def reset_password(request):

    if request.method == "POST":

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(
                request,
                "reset_password.html",
                {"error": "Passwords do not match"}
            )

        email = request.session.get("email")

        try:
            user = User.objects.get(email=email)
            user.set_password(password1)
            user.save()

            request.session.flush()

            return redirect("login")

        except User.DoesNotExist:
            return redirect("forgot_password")

    return render(request, "reset_password.html")

@api_view(['GET'])
def donation_api(request):
    donations = FoodDonation.objects.all()
    serializer = FoodDonationSerializer(donations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_donation_api(request):

    serializer = FoodDonationSerializer(data=request.data)

    if serializer.is_valid():

        donation = serializer.save()

        # Notify all NGO users
        ngo_profiles = UserProfile.objects.filter(role="NGO")

        for profile in ngo_profiles:
            Notification.objects.create(
                user=profile.user,
                message=f"New food donation request received: {donation.food_name}"
            )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )



@api_view(['PUT', 'PATCH'])
def update_donation_api(request, id):
    donation = get_object_or_404(FoodDonation, id=id)

    serializer = FoodDonationSerializer(
        donation,
        data=request.data,
        partial=(request.method == 'PATCH')
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['DELETE'])
def delete_donation_api(request, id):
    donation = get_object_or_404(FoodDonation, id=id)
    donation.delete()

    return Response(
        {"message": "Donation deleted successfully"},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def signup_api(request):
    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Signup Successful"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api(request):

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():

        user = serializer.validated_data["user"]

        return Response({
            "message": "Login Successful",
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_200_OK)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@login_required
def donation_detail(request, donation_id):
    donation = get_object_or_404(FoodDonation, id=donation_id)

    return render(
        request,
        "donation_detail.html",
        {"donation": donation}
    )

def request_donation(request, ngo_id):
    try:
        ngo = get_object_or_404(NGO, id=ngo_id)
        if request.method == "POST":
            donation_id = request.POST.get("donation_id")

            if not donation_id:
                return render(request, "request_failed.html")

            donation = get_object_or_404(
                FoodDonation,
                id=donation_id
            )

            DonationRequest.objects.create(
                donation=donation,
                ngo=ngo,
                status="Pending"
            )

            return render(request, "request_success.html", {
                "donation": donation,
                "ngo": ngo
            })

        return render(request, "request_donation.html", {
            "ngo": ngo,
            "donations": FoodDonation.objects.filter(
                status="Pending"
            )
        })

    except Exception:
        return render(request, "request_failed.html")

@login_required
def send_donation_request(request, ngo_id):

    ngo = get_object_or_404(NGO, id=ngo_id)

    # Donor ki food donation
    donation = FoodDonation.objects.filter(
        email=request.user.email
    ).order_by("-id").first()

    # Agar donor ne abhi tak food donation nahi ki
    if not donation:
        return render(
            request,
            "donation_request_failed.html",
            {
                "ngo": ngo,
                "message": "Please create a food donation first."
            }
        )

    # Same donation ke liye duplicate request check
    existing_request = DonationRequest.objects.filter(
        donor=request.user,
        ngo=ngo,
        food=donation
    ).first()

    if existing_request:
        return render(
            request,
            "donation_request_failed.html",
            {
                "ngo": ngo,
                "message": "You have already sent a request to this NGO."
            }
        )

    try:

        DonationRequest.objects.create(
            donor=request.user,
            ngo=ngo,
            food=donation
        )

        # NGO ko notification
        Notification.objects.create(
            user=ngo.user,
            message=(
                f"New donation request from "
                f"{request.user.username} for "
                f"{donation.food_name}"
            )
        )

        return render(
            request,
            "donation_request_success.html",
            {
                "ngo": ngo,
                "donation": donation
            }
        )

    except Exception:

      return render(
    request,
    "donation_request_failed.html",
    {"ngo_id": ngo_id}
)

def request_failed(request, ngo_id):
    return render(
        request,
        "donation_request_failed.html",
        {"ngo_id": ngo_id}
    )

@login_required
def ngo_donations(request):
    donations = FoodDonation.objects.all().order_by("-id")

    search = request.GET.get("search", "")
    category = request.GET.get("category", "")
    city = request.GET.get("city", "")

    if search:
        donations = donations.filter(
            food_name__icontains=search
        ) | donations.filter(
            donor_name__icontains=search
        ) | donations.filter(
            city__icontains=search
        )

    if category:
        donations = donations.filter(category=category)

    if city:
        donations = donations.filter(city__icontains=city)

    categories = FoodDonation.objects.values_list(
        "category", flat=True
    ).distinct()

    cities = FoodDonation.objects.values_list(
        "city", flat=True
    ).distinct()

    context = {
        "donations": donations,
        "categories": categories,
        "cities": cities,
        "search": search,
        "selected_category": category,
        "selected_city": city,
    }

    return render(request, "ngo_donations.html", context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import NGO


@login_required
def ngo_profile(request):
    ngo = NGO.objects.filter(
        email=request.user.email
    ).first()
    return render(
        request,
        "ngo_profile.html",
        {"ngo": ngo}
    )

@login_required
def edit_ngo_profile(request):

    # Same NGO that belongs to logged-in user
    ngo = NGO.objects.filter(
        email=request.user.email
    ).first()

    # Temporary fallback for your existing database
    if ngo is None:
        ngo = NGO.objects.first()

    if request.method == "POST":

        new_email = request.POST.get("email")

        ngo.name = request.POST.get("name")
        ngo.email = new_email
        ngo.phone = request.POST.get("phone")
        ngo.address = request.POST.get("address")
        ngo.city = request.POST.get("city")
        ngo.description = request.POST.get("description")

        if request.FILES.get("image"):
            ngo.image = request.FILES.get("image")

        ngo.save()

        # Keep Django User email and NGO email synchronized
        request.user.email = new_email
        request.user.save()

        return redirect("ngo_profile")

    return render(
        request,
        "edit_ngo_profile.html",
        {"ngo": ngo}
    )

@login_required
def impact_reports(request):

    total_donations = FoodDonation.objects.count()

    accepted_donations = FoodDonation.objects.filter(
        status="Accepted"
    ).count()

    completed_donations = FoodDonation.objects.filter(
        status="Completed"
    ).count()

    rejected_donations = FoodDonation.objects.filter(
        status="Rejected"
    ).count()

    context = {
        "total_donations": total_donations,
        "accepted_donations": accepted_donations,
        "completed_donations": completed_donations,
        "rejected_donations": rejected_donations,
    }

    return render(
        request,
        "impact_reports.html",
        context
    )

# @login_required
# def donation_requests(request):

#     ngo = NGO.objects.get(user=request.user)

#     requests = DonationRequest.objects.filter(
#         ngo=ngo,
#         status="Pending"
#     ).order_by("-created_at")

#     return render(
#         request,
#         "donation_requests.html",
#         {"requests": requests}
#     )

@login_required
def donation_requests(request):

    ngo = NGO.objects.filter(user=request.user).first()

    if not ngo:
        return render(
            request,
            "donation_requests.html",
            {"requests": [], "error": "NGO profile not found."}
        )

    requests = DonationRequest.objects.filter(
        ngo=ngo,
        status="Pending"
    ).order_by("-created_at")

    return render(
        request,
        "donation_requests.html",
        {"requests": requests}
    )

def calculate_food_priority(food):
    now = datetime.now().time()

    expiry = food.expiry_time

    # Expiry already passed
    if expiry <= now:
        return "Expired", "🔴 Food expiry time has passed"

    # Time difference in minutes
    now_minutes = now.hour * 60 + now.minute
    expiry_minutes = expiry.hour * 60 + expiry.minute

    remaining_minutes = expiry_minutes - now_minutes

    # Less than 2 hours
    if remaining_minutes <= 120:
        return "HIGH", "🔴 Expires very soon"

    # Less than 5 hours
    elif remaining_minutes <= 300:
        return "MEDIUM", "🟡 Expiry is approaching"

    else:
        return "LOW", "🟢 Enough time remaining"

def donation_list(request):

    donations = FoodDonation.objects.filter(
        status="Pending"
    )

    for donation in donations:
        priority, reason = calculate_food_priority(donation)

        donation.ai_priority = priority
        donation.ai_reason = reason

    return render(
        request,
        "donation_list.html",
        {
            "donations": donations
        }
    )



@login_required
def ai_recommendation(request):

    city = request.GET.get("city", "").strip()

    ngos = find_best_ngos(city)

    return render(
        request,
        "ai_recommendation.html",
        {
            "ngos": ngos,
            "city": city,
        }
    )
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "notification.html",
        {
            "notifications": notifications
        }
    )