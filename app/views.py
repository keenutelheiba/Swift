from django.shortcuts import render, redirect
from django.views import View
from app.models import CustomUser, Feedback, ContactForm, ContactNumber, Train, Station, ClassType, Booking, BookingDetail, BillingInfo, Payment, Ticket
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from app.forms import TrainForm
from datetime import timezone, datetime, timedelta
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.core.exceptions import ValidationError


# Create your views here.

# homepage view

class Home(View):
    def get(self, request):
        form = TrainForm
        return render(request, 'home.html', {'form': form})

        
# available train page view

class AvailableTrain(View):
    def get(self, request):
        try:
            # Get form data
            source = request.GET.get('rfrom')
            destination = request.GET.get('to')
            date = request.GET.get('date')
            class_type = request.GET.get('ctype')
            pa = request.GET.get('pa')
            pc = request.GET.get('pc')

            # Validate time formats
            departure_time = request.GET.get('departure_time')
            arrival_time = request.GET.get('arrival_time')

            if departure_time and arrival_time:
                try:
                    # Try to parse the times to validate format
                    datetime.strptime(departure_time, '%H:%M')
                    datetime.strptime(arrival_time, '%H:%M')
                except ValueError:
                    messages.error(request, "Invalid time format. Please use HH:MM format.")
                    return redirect('home')

            # Get available trains
            available_trains = Train.objects.filter(
                source=source,
                destination=destination
            )

            if not available_trains:
                messages.warning(request, "No trains available for this route.")
                return redirect('home')

            context = {
                'search': available_trains,
                'source': Station.objects.get(id=source),
                'destination': Station.objects.get(id=destination),
                'class_type': ClassType.objects.get(id=class_type),
                'date': date,
                'pa': pa,
                'pc': pc
            }

            return render(request, 'available_train.html', context)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('home')


#Booking page view

class Bookings(View):
    def get(self, request):
        if request.GET:

            user = request.user
            if user.is_authenticated:
                
                train = request.GET.get('train')
                source = request.GET.get('source')
                destination = request.GET.get('destination')
                date = request.GET.get('date')
                departure = request.GET.get('departure')
                arrival = request.GET.get('arrival')
                tp = request.GET.get('tp')
                pa = request.GET.get('pa')
                pc = request.GET.get('pc')
                ctype = request.GET.get('ctype')
                total_fare = request.GET.get('total_fare')

                fare_each = ClassType.objects.get(name=ctype)

                # this is for booking seat according to train seat capacity

                ticket = Ticket.objects.filter(train_name=train, travel_date=date)
                # if ticket.count() < 30:
                #     print(ticket.count())
                available_seat = 30 - ticket.count()
                print(available_seat)
                tp = int(tp)
                if available_seat >= tp:

                    return render(request, 'booking.html', {'train':train, 'source':source, 'destination':destination, 'date':date, 'departure':departure, 'arrival':arrival, 'tp':tp, 'pa':pa, 'pc':pc, 'ctype':ctype, 'total_fare':total_fare, 'fare_each':fare_each})
                else:
                    messages.warning(request, f"sorry! {available_seat} seat is available for this train. Try again!")
                    return redirect('home')
                
                # this is for booking seat according to train seat capacity (end)
                # else:
                #     messages.warning(request, "sorry! enough seat is not available for this train. Try again!")
                #     return redirect('home')
            else:
                messages.warning(request, "login first to book train")
                return redirect('login')
        else:
            messages.warning(request, 'find a train first!')
            return redirect('home')

    def post(self, request):
        try:
            # Get all form data first
            user = request.user
            train = request.POST['train']
            source = request.POST['source']
            destination = request.POST['destination']
            travel_date = request.POST['travel_date']
            travel_time = request.POST['departure']
            arrival = request.POST['arrival']
            nop = request.POST['tp']
            adult = request.POST['pa']
            child = request.POST['pc']
            class_type = request.POST['ctype']
            fpp = request.POST['fpp']
            total_fare = request.POST['total_fare']
            email = request.POST['email']
            phone = request.POST['phone']
            pay_method = request.POST['ptype']
            pay_phone = request.POST['pay_phone']
            trxid = request.POST['trxid']

            # Convert 12-hour format to 24-hour format
            if isinstance(travel_time, str):
                travel_time = travel_time.replace('.', '')
                try:
                    parsed_time = datetime.strptime(travel_time, '%I:%M %p')
                    travel_time = parsed_time.strftime('%H:%M')
                except ValueError:
                    pass

            # Create datetime object
            travel_datetime = f"{travel_date} {travel_time}"
            travel_dt = datetime.strptime(travel_datetime, '%Y-%m-%d %H:%M')

            # Create booking
            booking = Booking(
                user=user,
                travel_dt=travel_dt,
                status='Confirmed'
            )
            booking.save()

            # Create booking detail
            booking_detail = BookingDetail(
                booking=booking,
                train=train,
                source=source,
                destination=destination,
                travel_date=travel_date,
                travel_time=travel_time,
                travel_dt=travel_dt,
                nop=nop,
                adult=adult,
                child=child,
                class_type=class_type,
                fpp=fpp,
                total_fare=total_fare
            )
            booking_detail.save()

            # Create billing info
            billing_info = BillingInfo(
                booking=booking,
                user=user,
                email=email,
                phone=phone
            )
            billing_info.save()

            # Create payment
            payment = Payment(
                booking=booking,
                user=user,
                pay_amount=total_fare,
                pay_method=pay_method,
                phone=pay_phone,
                trxid=trxid,
                status='Completed'
            )
            payment.save()

            # Generate tickets
            nop = int(nop)
            for i in range(nop):
                ticket = Ticket(
                    booking=booking,
                    user=user,
                    phone=phone,
                    source=source,
                    destination=destination,
                    departure=travel_time,
                    travel_date=travel_date,
                    train_name=train,
                    class_type=class_type,
                    fare=fpp
                )
                ticket.save()

            messages.success(request, 'Booking successful!')
            return redirect('booking_history')

        except Exception as e:
            print(f"Booking error: {e}")  # For debugging
            messages.error(request, f'Booking failed: {str(e)}')
            return redirect('home')


# booking history page view

class BookingHistory(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, "Please login first")
            return redirect('login')
            
        try:
            # Get bookings based on user type
            if request.user.is_superuser:
                bookings = Booking.objects.select_related('user').prefetch_related(
                    'details', 'ticket_set'
                ).all().order_by('-booking_date')
            else:
                bookings = Booking.objects.select_related('user').prefetch_related(
                    'details', 'ticket_set'
                ).filter(user=request.user).order_by('-booking_date')
            
            # Process booking data
            booking_data = []
            for booking in bookings:
                booking_detail = booking.details.first()
                ticket = booking.ticket_set.first()  # Get associated ticket
                if booking_detail:
                    data = {
                        'id': booking.id,
                        'user': booking.user,
                        'train': booking_detail.train,
                        'source': booking_detail.source,
                        'destination': booking_detail.destination,
                        'travel_date': booking_detail.travel_date,
                        'status': booking.status,
                        'booking_date': booking.booking_date,
                        'has_ticket': ticket is not None  # Check if ticket exists
                    }
                    booking_data.append(data)
            
            return render(request, 'booking_history.html', {'booking': booking_data})
            
        except Exception as e:
            messages.error(request, f"Error retrieving booking history: {str(e)}")
            return redirect('home')


# booking detail page view

class BookingDetails(View):
    def get(self, request, pk):
        if request.user.is_authenticated:
            try:
                # Get the booking and all related objects
                booking = Booking.objects.get(id=pk, user=request.user)
                booking_detail = BookingDetail.objects.get(booking=booking)
                billing_info = BillingInfo.objects.get(booking=booking)
                payment = Payment.objects.get(booking=booking)
                
                # Debug print statements
                print(f"Found booking: {booking.id}")
                print(f"Found booking detail: {booking_detail.id}")
                print(f"Found billing info: {billing_info.id}")
                print(f"Found payment: {payment.id}")
                
                context = {
                    'booking_detail': booking_detail,
                    'billing': billing_info,
                    'payment': payment
                }
                return render(request, 'booking_detail.html', context)
                
            except Booking.DoesNotExist:
                print("Booking not found")
                messages.warning(request, "Booking not found!")
                return redirect('booking_history')
            except BookingDetail.DoesNotExist:
                print("Booking detail not found")
                messages.warning(request, "Booking details not found!")
                return redirect('booking_history')
            except BillingInfo.DoesNotExist:
                print("Billing info not found")
                messages.warning(request, "Billing information not found!")
                return redirect('booking_history')
            except Payment.DoesNotExist:
                print("Payment not found")
                messages.warning(request, "Payment information not found!")
                return redirect('booking_history')
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                messages.error(request, "An error occurred while retrieving booking details")
                return redirect('booking_history')
        return redirect('login')


# ticket page view

class Tickets(View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            bookings = Booking.objects.get(id=pk)
            if user == bookings.user:
                ticket = Ticket.objects.filter(booking=bookings)
                return render(request, 'ticket.html', {'ticket':ticket, 'bookings':bookings})
            else:
                messages.warning(request, 'Invalid booking id!')
                return redirect('booking_history')
        else:
            return redirect('login')


# cancel booking view

class CancelBooking(View):
    def post(self, request):
        try:
            booking_id = request.POST['booking_id']
            booking = Booking.objects.get(id=booking_id, user=request.user)
            booking.delete()
            messages.success(request, 'Your booking has been cancelled successfully')
        except Exception as e:
            print(f"Cancellation error: {e}")
            messages.error(request, 'Failed to cancel booking')
        return redirect('booking_history')


# signup for user

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validation checks
        if not all([first_name, last_name, username, email, phone, password1, password2]):
            messages.warning(request, "All fields are required")
            return redirect('signup')

        if password1 != password2:
            messages.warning(request, "Passwords don't match")
            return redirect('signup')

        # Check if username already exists
        try:
            if CustomUser.objects.filter(username=username).exists():
                messages.warning(request, "Username not available")
                return redirect('signup')
            
            # Create new user
            new_user = CustomUser.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password1
            )
            new_user.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('signup')

    return render(request, 'signup.html')


# login for admin and user

def user_login(request):
    check = request.user
    if check.is_authenticated:
        return redirect('home')
    else:
            
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username,password=password)
            
            if user is not None:
                login(request,user)
                messages.success(request,"successful logged in")
                return redirect('home')
            else:
                messages.warning(request,"Incorrect username or password")
                return redirect('login')

    response = render(request, 'login.html')
    return HttpResponse(response)


# contact page view

class Contact(View):
    def get(self, request):
        contact = ContactNumber.objects.all()
        return render(request, 'contact.html', {'contact': contact})

    def post(self, request):
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        if name == '' or email == '' or message == '':
            messages.warning(request, 'Please fillup all the fields to send message!')
            return redirect('contact')
        
        else:
            form = ContactForm(name=name, email=email, message=message)
            form.save()
            messages.success(request, 'You have successfully sent the message!')  
            return redirect('contact')


# feedback page view

class Feedbacks(View):
    def get(self, request):
        feedback = Feedback.objects.all().order_by('-created_at')
        return render(request, 'feedback.html', {'feedback': feedback})

    def post(self, request):
        if request.user.is_authenticated:
            feedback_text = request.POST.get('feedback')
            image = request.FILES.get('image')
            
            if feedback_text:
                feedback = Feedback(
                    name=f"{request.user.first_name} {request.user.last_name}",
                    feedback=feedback_text,
                    image=image
                )
                feedback.save()
                messages.success(request, "Thank you for your feedback!")
            return redirect('feedback')
        else:
            messages.warning(request, "Please login first to give feedback")
            return redirect('login')


# verify ticket page view

class VerifyTicket(View):
    def get(self, request):
        trains = Train.objects.all()
        if request.GET:

            train = request.GET.get('train')
            date = request.GET.get('date')
            tid = request.GET.get('tid')

            tid = str(tid)
            date = str(date)

            ticket = None

            try:
                ticket = Ticket.objects.get(id=tid, train_name=train, travel_date=date)
                ticket.id = str(ticket.id)
                ticket.travel_date = str(ticket.travel_date)
                return render(request, 'verify_ticket.html', {'train':trains, 'ticket':ticket})

            except:
                ticket = None
                return render(request, 'verify_ticket.html', {'train':trains, 'ticket':ticket})
            
        else:
            return render(request, 'verify_ticket.html', {'train':trains})

        return render(request, 'verify_ticket.html', {'train':trains})


# profile page view for user

class Profile(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'profile.html')
        else:
            messages.warning(request, "Please login first to view profile")
            return redirect('login')
            
    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            
            try:
                # Handle photo upload
                if 'photo' in request.FILES:
                    photo = request.FILES['photo']
                    
                    # Delete old photo if it exists
                    if user.photo:
                        if os.path.isfile(user.photo.path):
                            os.remove(user.photo.path)
                    
                    # Save new photo
                    user.photo = photo
                
                # Update other user information
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.phone = phone
                
                user.save()
                messages.success(request, "Profile updated successfully!")
                
            except Exception as e:
                messages.error(request, f"Error updating profile: {str(e)}")
                
            return redirect('profile')
        else:
            messages.warning(request, "Please login first to update profile")
            return redirect('login')

def search_stations(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
        
    stations = Station.objects.filter(
        Q(name__icontains=query) | Q(place__icontains=query)
    )[:10]
    
    results = [
        {
            'id': station.id,
            'name': station.name,
            'place': station.place
        }
        for station in stations
    ]
    return JsonResponse(results, safe=False)