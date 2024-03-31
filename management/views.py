from decimal import Decimal
import os
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import AllStudent,Course, Installment
from datetime import date
import pandas as pd
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from django.urls import reverse
from django.utils import timezone





def payment_method(request):
    return render(request, 'paymentMethod.html')


def search_student(request):
    return render(request, 'searchStudent.html')




def index(request):
    try:
        unpaid_students = AllStudent.objects.get_unpaid_students()
        print(unpaid_students)  # Debugging line
        return render(request, 'index.html', {'student': unpaid_students})
    except Exception as e:
        return HttpResponseServerError("An error occurred: " + str(e))

def addmission(request):
    try:
        students = AllStudent.objects.all()
        courses = Course.objects.all()

        if request.method == "POST":
            # Retrieve form data
            name = request.POST.get('name')
            mobile = request.POST.get('mobile')
            nid = request.POST.get('nid')
            nationality = request.POST.get('nationality')
            courses_id = request.POST.get('courses')
            country = request.POST.get('country')
            date = request.POST.get('date')
            
            # Calculate tax based on the country
            tax = Decimal('0')
            if country != "Saudi Arabia":
                tax = Decimal('0.5')  # Set the tax rate to 50% for countries other than Saudi Arabia


            # Create a new AllStudent instance
            new_student = AllStudent(
                name=name,
                nid_card=nid,
                phone_number=mobile,
                nationality=nationality,
                country=country,
                addmission_date=date,
                course_id=courses_id,
                tax=tax,
            
                # Add other fields as needed
            )
            # Calculate total amount including tax
            total = new_student.course.course_fee + new_student.course.admission_fee
            total_with_tax = total + (tax * total)  # Adding tax to the total amount
            
            installment_per_month = (new_student.course.course_fee + (tax * new_student.course.course_fee))/30; # Adding tax to the total course amount
            

            # Pass the student data to the confirmation page without saving it yet
            return render(request, 'confirmation_page.html', {'student': new_student, 'total': total_with_tax, 'per_month_installment_amount':installment_per_month})
        
        return render(request, 'addmissionForm.html', {'students': students, 'course': courses})
    except Exception as e:
        return HttpResponseServerError("An error occurred: " + str(e))


def save_confirmation(request):
    if request.method == 'POST':
        # Retrieve the data from the confirmation form
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        nid = request.POST.get('nid')
        nationality = request.POST.get('nationality')
        courses_id = request.POST.get('courses')
        country = request.POST.get('country')
        date = request.POST.get('date')
        tax = request.POST.get('tax')
        addmision_fee = request.POST.get('admission_fee')
        total_with_tax = request.POST.get('total_with_tax')
        installment_per_month = request.POST.get('installment_per_month')

        # Validate the data
        if not all([name, mobile, nid, nationality, courses_id, country, date, tax, addmision_fee, total_with_tax, installment_per_month]):
            return HttpResponseBadRequest("Missing required fields")

        try:
            # Convert necessary fields to their appropriate types
            courses_id = int(courses_id)
            addmision_fee = float(addmision_fee)
            total_with_tax = float(total_with_tax)
            installment_per_month = float(installment_per_month)

            # Create a new AllStudent instance
            new_student = AllStudent(
                name=name,
                nid_card=nid,
                phone_number=mobile,
                nationality=nationality,
                country=country,
                addmission_date=date,
                course_id=courses_id,
                tax=tax,
                addmision_fee=addmision_fee,
                total_payable_amount=total_with_tax,
                per_month_installment_amount=installment_per_month,
                total_paid_amount=addmision_fee,
                # Add other fields as needed
            )

            # Save the student data to the database
            new_student.save()

            # Redirect to a success page
            return render(request, 'confirmation_success.html')
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid data format")

    # Redirect back to the admission form if accessed directly
    return redirect('addmission')

def cancel_confirmation(request):
    try:
        # Handle cancellation by redirecting back to the admission form
        return HttpResponse(status=204)  # HTTP 204 No Content
    except Exception as e:
        # Handle any exceptions and return a bad request response
        return HttpResponseBadRequest(f"An error occurred: {e}")


# Function to generate a unique transaction ID

def generate_transaction_id(student, installment_number):
    student_id_part = str(student.id).zfill(6)
    installment_id_part = str(installment_number).zfill(6)
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    transaction_id = f"{student_id_part}-{installment_id_part}-{random_part}"
    return transaction_id


def fee_deposite(request, pk):
    try:
        student_instance = get_object_or_404(AllStudent, nid_card=pk)

        # Example of retrieving installments for a student
        installments = student_instance.installments.all()

        if installments:
            # Get the latest installment
            latest_installment = installments.order_by('-installment_number').first()
            # Calculate the next installment number
            next_installment_number = latest_installment.installment_number + 1 if latest_installment else 1
            # Calculate the next installment date based on the last installment's paying date
            next_installment_date = latest_installment.installment_date.replace(day=datetime.now().day) + timedelta(days=30) if latest_installment else datetime.now().replace(day=datetime.now().day)
        else:
            # If no installments exist, set the next installment number to 1 and the next installment date to the beginning of the next month
            next_installment_number = 1
            next_installment_date = datetime.now().replace(day=datetime.now().day)

        next_installment_date_formatted = next_installment_date.strftime('%Y-%m-%d')  # Format the date as 'YYYY-MM-DD'

        # Example of determining discount period
        payment_date_discount = 0
        last_month_end = datetime.now().replace(day=1) - timedelta(days=1)
        discount_period_start = last_month_end.replace(day=25)
        discount_period_end = datetime.now().replace(day=10)
        if discount_period_start <= datetime.now() <= discount_period_end:
            payment_date_discount = Decimal('30')  # Apply a discount of 30% (you can adjust this value)

        # Example of generating transaction ID
        transaction_id = generate_transaction_id(student_instance, next_installment_number)

        context = {
            "student": student_instance,
            "course_fee": float(student_instance.course.course_fee) if student_instance.course.course_fee is not None else 0.0,
            "course_name": student_instance.course.name,
            "installment_number": next_installment_number,
            "monthly_installment_amount": float(student_instance.per_month_installment_amount) if student_instance.per_month_installment_amount is not None else 0.0,
            "payment_date_discount": float(payment_date_discount),
            "transaction_id": transaction_id,
            "installment_date": next_installment_date,  # Pass the formatted date to the template
            "next_installment_date": next_installment_date_formatted,  # Pass the formatted date to the template
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(context)
        else:
            return render(request, 'feeDeposite.html', context)
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")


    


def show_deposit_information(request):
    try:
        if request.method == 'POST':
            try:
                # Retrieve data from the POST request
                student_id = request.POST.get('student_id')
                payment_date_discount_percentage = Decimal(request.POST.get('payment_date_discount', '0'))
                transaction_id = request.POST.get('transaction_id', '')
                payment_method = request.POST.get('payment_method', '')
                installment_date_str = request.POST.get('installment_date', '')
                comment = request.POST.get('comment', '')
                installment_number = int(request.POST.get('installment_number',))
                provide_installment_amount = Decimal(request.POST.get('monthly_installment_amount',))

                # Parse installment date string into datetime object
                installment_date = datetime.strptime(installment_date_str, '%Y-%m-%d').date()

                # Retrieve the student instance
                student_instance = get_object_or_404(AllStudent, nid_card=student_id)

                # Check if the student has already paid an installment this month
                existing_installment_this_month = Installment.objects.filter(
                    student=student_instance,
                    installment_date__year=installment_date.year,
                    installment_date__month=installment_date.month
                ).exists()

                if existing_installment_this_month:
                    raise ValueError("The student has already paid an installment this month.")
                

                # Check if any extra amount is provided
                if provide_installment_amount is not None and student_instance.extra_money is not None:
                    extra_money = (provide_installment_amount + student_instance.extra_money) %  student_instance.per_month_installment_amount
                    student_instance.extra_money = extra_money
                    student_instance.save()


                if provide_installment_amount is not None and student_instance.extra_money is not None:
                    total_extra_money = provide_installment_amount + student_instance.extra_money
                    can_provided_installment_of_this_deposit = max(0, total_extra_money // student_instance.per_month_installment_amount)
                else:
                    can_provided_installment_of_this_deposit = 0


                # Calculate the total installment amount after discount
                per_month_installment_amount = student_instance.per_month_installment_amount

                payment_date_discount = (payment_date_discount_percentage / 100) * per_month_installment_amount
                total_installment_amount = per_month_installment_amount - payment_date_discount

                print(can_provided_installment_of_this_deposit)

                context = {
                    "student": student_instance,
                    "course_fee": float(student_instance.course.course_fee) if student_instance.course.course_fee is not None else 0.0,
                    "course_name": student_instance.course.name,
                    "payment_date_discount": payment_date_discount_percentage,
                    "transaction_id": transaction_id,
                    "payment_method": payment_method,
                    "installment_date": installment_date_str,
                    "comment": comment,
                    "normal_date": installment_date,
                    "installment_number": installment_number,
                    "total_installment_amount": "{:.2f}".format(total_installment_amount),
                    "provided_amount": provide_installment_amount,
                    "total_installment_of_this_deposit": can_provided_installment_of_this_deposit,
                }

                return render(request, 'diposit_confirmation_page.html', context)

            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})

        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})
        
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")



def confirm_deposit(request):
    try:
        if request.method == 'POST':
            try:
                # Retrieve data from the POST request
                student_id = request.POST.get('student')
                installment_amount = Decimal(request.POST.get('installment_amount'))
                installment_number = int(request.POST.get('installment_number'))
                comment = request.POST.get('comment', '')
                payment_method = request.POST.get('payment_method', '')
                discount_percentage = Decimal(request.POST.get('discount'))

                # Retrieve the student instance
                student_instance = get_object_or_404(AllStudent, nid_card=student_id)

                # Example of retrieving installments for a student
                installments = student_instance.installments.all()

                for number in range(int(request.POST.get('total_installment_of_this_deposit', 0))):
                    # Calculate the next installment number
                    next_installment_number = 1
                    if installments.exists():
                        latest_installment = installments.order_by('-installment_number').first()
                        next_installment_number = latest_installment.installment_number + 1

                    # Calculate the next installment date
                    next_installment_date = datetime.now().replace(day=datetime.now().day)
                    if installments.exists():
                        latest_installment_date = latest_installment.installment_date
                        next_installment_date = latest_installment_date.replace(day=datetime.now().day) + timedelta(days=30)

                    # Calculate the discount amount
                    per_month_installment_amount = student_instance.per_month_installment_amount
                    payment_date_discount = discount_percentage / Decimal(100) * per_month_installment_amount
                    total_installment_amount = round(per_month_installment_amount - payment_date_discount, 2)

                    # Generate transaction ID
                    transaction_id = generate_transaction_id(student_instance, next_installment_number)

                    # Save the installment
                    installment = Installment.objects.create(
                        student=student_instance,
                        installment_amount=total_installment_amount,
                        installment_number=next_installment_number,
                        payment_method=payment_method,
                        installment_date=next_installment_date,
                        transaction_id=transaction_id,
                        discount=payment_date_discount,
                        comment=comment
                    )

                    # Update the total_paid_amount in student instance
                    student_instance.total_paid_amount += total_installment_amount
                    student_instance.save()

                return redirect('fee_deposite', pk=student_id)

            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid request method'})

    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")






def pre_search_deposit(request):
    try:
        nid_card_number = request.GET.get('nidCardNumber', '')
        student_name = request.GET.get('studentName', '')
        level = request.GET.get('level', '')
        course = request.GET.get('course', '')

        # Initialize the queryset with all students
        queryset = AllStudent.objects.all()

        # Filter the queryset based on the provided search parameters
        if nid_card_number:
            queryset = queryset.filter(nid_card__icontains=nid_card_number)
        if student_name:
            queryset = queryset.filter(name__icontains=student_name)
        if level:
            queryset = queryset.filter(class_or_level__icontains=level)
        if course:
            queryset = queryset.filter(course__name__icontains=course)  # Assuming 'course' is a ForeignKey to Course model

        # Order the results by the creation date in descending order
        queryset = queryset.order_by('-join_date')

        students = list(queryset)

        # Pass the filtered queryset to the template
        context = {
            'students': students,
            'nid_card_number': nid_card_number,
            'student_name': student_name,
            'level': level,
            'course': course,
        }

        if students:
            print(context['students'][0].name)

        return render(request, 'preFeeDeposit.html', context)
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")


def statement(request, pk):
    try:
        student = get_object_or_404(AllStudent, nid_card=pk)
        installments = student.installments.all()  # Fetch all installments for the student

        context = {
            "student": student,
            "course_fee": student.course.course_fee,
            "date": date.today(),
            "installments": installments  # Pass installments to the template
        }
        return render(request, 'invoice.html', context)
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")


def search_statement(request):
    try:
        nid_card_number = request.GET.get('nidCardNumber', '')
        student_name = request.GET.get('studentName', '')
        level = request.GET.get('level', '')
        course = request.GET.get('course', '')

        # Initialize the queryset with all students
        queryset = AllStudent.objects.all()

        # Filter the queryset based on the provided search parameters
        if nid_card_number:
            queryset = queryset.filter(nid_card__icontains=nid_card_number)
        if student_name:
            queryset = queryset.filter(name__icontains=student_name)
        if level:
            queryset = queryset.filter(class_or_level__icontains=level)
        if course:
            queryset = queryset.filter(course__name__icontains=course)  # Assuming 'course' is a ForeignKey to Course model

        # Pass the filtered queryset to the template
        context = {
            'students': queryset,
            'nid_card_number': nid_card_number,
            'student_name': student_name,
            'level': level,
            'course': course,
        }
        print(context['students'][0].name)

        return render(request, 'searchStatement.html', context)
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")



def search_view(request):
    try:
        # Retrieve search parameters from the request
        nid_card_number = request.GET.get('nidCardNumber', '')
        student_name = request.GET.get('studentName', '')
        level = request.GET.get('level', '')
        course = request.GET.get('course', '')

        # Initialize the queryset with all students
        queryset = AllStudent.objects.all()

        # Filter the queryset based on the provided search parameters
        if nid_card_number:
            queryset = queryset.filter(nid_card__icontains=nid_card_number)
        if student_name:
            queryset = queryset.filter(name__icontains=student_name)
        if level:
            queryset = queryset.filter(class_or_level__icontains=level)
        if course:
            queryset = queryset.filter(course__name__icontains=course)  # Assuming 'course' is a ForeignKey to Course model

        # Pass the filtered queryset to the template
        context = {
            'students': queryset,
            'nid_card_number': nid_card_number,
            'student_name': student_name,
            'level': level,
            'course': course,
        }
        print(queryset)

        return render(request, 'searchView.html', context)  
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")



def manage_database(request):
    try:
        student = AllStudent.objects.all();
        return render(request, 'manageDatabase.html',{'student':student})
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")




def upload_file(request):
    try:
        if request.method == 'POST' and request.FILES['file']:
            file = request.FILES['file']
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
                for index, row in df.iterrows():
                    AllStudent.objects.create(
                        name=row['Name'],
                        nid_card=row['NID Card'],
                        phone_number=row['Phone Number'],
                        nationality=row['Nationality'],
                        country=row['Country'],
                        addmission_date=row['Admission Date'],
                        course = Course.objects.get(pk=row['Course']),
                        tax = row['Tax'],
                        class_or_level = row['Class or Level'],
                        addmision_fee = row['Admission Fee'],
                        per_month_installment_amount = row['Monthly Installment Amount'],
                        total_paid_amount = row['Total Paid Amount'],
                        extra_money = row['Extra Money'],
                        total_payable_amount = row['Total Payable Amount'],
                        # Add other fields as necessary
                    )
                return redirect('upload_success')
            else:
                return render(request, 'upload_failure.html')
        return render(request, 'importData.html')
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")
    


def upload_installments(request):
    try:
        if request.method == 'POST' and request.FILES.get('file'):
            excel_file = request.FILES['file']
            
            # Specify the date columns and their format
            date_columns = ['Installment Date']
            date_format = "%Y-%m-%d"  # Adjust the format as needed

            # Read the Excel file with the specified date format
            try:
                df = pd.read_excel(excel_file, parse_dates=date_columns, date_parser=lambda x: pd.to_datetime(x, format=date_format))
            except Exception as e:
                return render(request, 'upload_installments.html', {'error_message': str(e)})
            
            for index, row in df.iterrows():
                nid_card = row['NID Card']
                try:
                    student = AllStudent.objects.get(nid_card=nid_card)
                except AllStudent.DoesNotExist:
                    return render(request, 'upload_installments.html', {'error_message': f"Student with NID Card {nid_card} does not exist."})

                # Check if 'Comment' column exists before accessing its value
                comment = row.get('Comment', None)

                installment = Installment(
                    student=student,
                    installment_amount=row['Installment Amount'],
                    installment_number=row['Installment Number'],
                    comment=comment,  # Use the value if available, otherwise None
                    payment_method=row['Payment Method'],
                    installment_date=row['Installment Date'],
                    transaction_id=row['Transaction ID'],
                    discount=row['Discount']
                )
                installment.save()

            return redirect('upload_success')
        return render(request, 'upload_installments.html')
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")
    

def search_by_admission_year(request):
    try:
        if request.method == 'POST':
            admission_year = request.POST.get('admission_year')
            if admission_year:
                students = AllStudent.objects.filter(addmission_date__year=admission_year)
                context = {'students': students, 'admission_year': admission_year}
                return render(request, 'search_by_admission_year.html', context)
            else:
                return render(request, 'search_by_admission_year.html')
        else:
            return render(request, 'search_by_admission_year.html')
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")
    

def upload_success(request):
    return render(request, 'upload_success.html')

def upload_failed(request):
    return render(request, 'upload_failure.html')

def level_up_students(request):
    try:
        if request.method == 'POST':
            admission_year = request.POST.get('admission_year')
            if admission_year:
                students = AllStudent.objects.filter(addmission_date__year=admission_year)
                for student in students:
                    # Assuming class_or_level is the field representing the level
                    student.class_or_level += 1
                    student.save()
        return redirect(reverse('level_up_success'))
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")

def level_up_success(request):
    return render(request, 'level_up_success.html')

def search_report(request):
    return render(request, 'search_report.html')


def pre_report(request):
    try:
        nid_card_number = request.GET.get('nidCardNumber', '')
        student_name = request.GET.get('studentName', '')
        level = request.GET.get('level', '')
        course = request.GET.get('course', '')

        # Initialize the queryset with all students
        queryset = AllStudent.objects.all()

        # Filter the queryset based on the provided search parameters
        if nid_card_number:
            queryset = queryset.filter(nid_card__icontains=nid_card_number)
        if student_name:
            queryset = queryset.filter(name__icontains=student_name)
        if level:
            queryset = queryset.filter(class_or_level__icontains=level)
        if course:
            queryset = queryset.filter(course__name__icontains=course)  # Assuming 'course' is a ForeignKey to Course model

        # Order the results by the creation date in descending order
        queryset = queryset.order_by('-join_date')

        students = list(queryset)

        # Pass the filtered queryset to the template
        context = {
            'students': students,
            'nid_card_number': nid_card_number,
            'student_name': student_name,
            'level': level,
            'course': course,
        }

        if students:
            print(context['students'][0].name)

        return render(request, 'preReportPage.html', context)
    
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")



def select_period(request):
    try:
        if request.method == 'GET':
            period = request.GET.get('period')
            students = None

            preoders = "";

            if period == 'last_7_days':
                start_date = timezone.now() - timedelta(days=7)
                students = AllStudent.objects.filter(installments__installment_date__gte=start_date).distinct()
                preoders = "Last 7 Days"
            elif period == 'last_1_month':
                start_date = timezone.now() - timedelta(days=30)
                students = AllStudent.objects.filter(installments__installment_date__gte=start_date).distinct()
                preoders = "Last 1 Month"
            elif period == 'last_6_months':
                start_date = timezone.now() - timedelta(days=6*30)
                students = AllStudent.objects.filter(installments__installment_date__gte=start_date).distinct()
                preoders = "Last 6 Months"
            elif period == 'last_1_year':
                start_date = timezone.now() - timedelta(days=365)
                students = AllStudent.objects.filter(installments__installment_date__gte=start_date).distinct()
                preoders = "Last 1 Year"
            
            print(preoders)

            return render(request, 'show_students_by_period.html', {'students': students, 'period': preoders})
        else:
            return render(request, 'error_page.html', {'message': 'Invalid request method'})
        
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")
    

def download_student_info_demo(request):
    try:
         # Open the file from static folder
        with open("static/demo_files/student_info_demo.xlsx", 'rb') as f:
            file_content = f.read()

        # Prepare a downloadable response with appropriate headers
        response = HttpResponse(file_content, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=student_info_demo.xlsx'

        return response
                
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")


def download_student_installment_demo(request):
    try:
         # Open the file from static folder
        with open("static/demo_files/student_installment_demo.xlsx", 'rb') as f:
            file_content = f.read()

        # Prepare a downloadable response with appropriate headers
        response = HttpResponse(file_content, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=student_installment_demo.xlsx'

        return response
                
    except Exception as e:
        return HttpResponseBadRequest(f"An error occurred: {e}")
    