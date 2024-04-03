from django.shortcuts import render, redirect ,get_object_or_404
from .forms import SignUpForm, LoginForm ,StudentProfileForm
from django.contrib.auth import authenticate, login
from .models import RequestToAdmin  ,Folder,File ,Student 
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from PortFolio.models import User 
from django.db.models import Count 
from django.http import HttpResponse
from .models import ProfileVisitLink
import uuid
from django.urls import reverse
from django.utils.crypto import get_random_string
import qrcode
from io import BytesIO
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image


def home(request):
    if request.user.is_authenticated:
        try:
            student = request.user.student 
            profile_visit_link = ProfileVisitLink.objects.filter(user=request.user).last()
            generated_link = profile_visit_link.generated_link if profile_visit_link else None
            return render(request, 'home.html', {'student': student, 'generated_link': generated_link})
        except Student.DoesNotExist:
            return render(request, 'home.html', {'error_message': 'Student profile not found'})
    else:
        return render(request, 'home.html', {'error_message': 'Please log in'})


def delete_profile_image(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        try:
            profile = UserProfile.objects.get(id=profile_id)
            # Clear the profile image field and save the profile
            profile.profile_image = None
            profile.save()
            return redirect('profile')
        except UserProfile.DoesNotExist:
            pass
    return redirect('profile')

@login_required
def dashboard(request):
    try:
        student = request.user.student
        user_id = request.user.id
        folders_with_file_count = Folder.objects.filter(folderuser_id=user_id).annotate(num_files=Count('file'))
        folder_count = Folder.objects.filter(folderuser_id=user_id).count()
        file_count = File.objects.filter(folder__folderuser_id=user_id).count()
        profile_visit_link = ProfileVisitLink.objects.filter(user=request.user).last()
        generated_link = profile_visit_link.generated_link if profile_visit_link else None

        context = {
            'student': student,
            'user': request.user,
            'folders_with_file_count': folders_with_file_count,
            'folder_count': folder_count,
            'file_count': file_count,
            'generated_link': generated_link,
        }
        return render(request, 'dashboard.html', context)
    except ObjectDoesNotExist:
        error_message = 'Student profile not found'
        return render(request, 'dashboard.html', {'error_message': error_message})

def activity(request):  
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            folder = Folder.objects.filter(folderuser=request.user)
            profile_visit_link = ProfileVisitLink.objects.filter(user=request.user).last()
            generated_link = profile_visit_link.generated_link if profile_visit_link else None

            context = {'folder': folder, 'student': student, 'user': request.user,
                       'generated_link': generated_link}
            return render(request, 'activity.html', context)
        except ObjectDoesNotExist:
            return render(request, 'error.html', {'error_message': 'Student matching query does not exist.'})
    else:
        return redirect('homepage')

# def activity(request):
#     student = Student.objects.get(user=request.user)
#     context = {
#         'student': student,
#         'user': request.user,
#     }
#     return render(request ,'activity.html',context)

# def activity(request):  
#     if request.user.is_authenticated:
#         student = Student.objects.get(user=request.user)
#         folder = Folder.objects.filter(folderuser=request.user)
#         context = {'folder':folder , 'student': student,
#             'user': request.user,}
#         return render(request,'activity.html',context)
#     else:
#         return redirect('homepage')

def resume(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
        'user': request.user,
    }
    return render(request ,'resume.html',context)

def waiting_page(request):
    return render(request, 'waiting_page.html')

def decline_page(request):
    return render(request, 'decline_page.html')

def admin(request):
    # Retrieve requests from students
    requests = RequestToAdmin.objects.all()
    return render(request, 'staff/staffadmin.html', {'requests': requests})

def approve_request(request, request_id):
    request_object = RequestToAdmin.objects.get(id=request_id)
    student = request_object.student
    student.request_approved = True
    student.request_declined = False
    student.save()
    request_object.delete()  
    return redirect('adminpage')

def decline_request(request, request_id):
    request_object = RequestToAdmin.objects.get(id=request_id)
    student = request_object.student
    student.request_approved = False
    student.request_declined = True
    student.save()
    # You may want to add additional logic here, such as sending notifications to the student
    request_object.delete()  # Delete the request after it's declined
    return redirect('adminpage')
    
def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.role = form.cleaned_data['role']
            user.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login_view')
        else:
            messages.error(request, 'Registration failed. Please check the form.')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def login_view1(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'admin':
                    return redirect('adminpage')
                elif user.role == 'student':
                    existing_request = RequestToAdmin.objects.filter(student=user).exists()
                    if not existing_request:
                        RequestToAdmin.objects.create(student=user, message="Please process my request.")
                    if user.request_approved:
                        return redirect('homepage')
                    elif user.request_declined:
                        return redirect('login_view') 
                    else:
                        return redirect('decline_page')
                else:
                    pass
            else:
                pass
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'admin':
                    messages.success(request, 'Admin login successful.')
                    return redirect('adminpage')
                elif user.role == 'student':
                    existing_request = RequestToAdmin.objects.filter(student=user).exists()
                    if not existing_request:
                        RequestToAdmin.objects.create(student=user, message="Please process my request.")
                    if user.request_approved:
                        messages.success(request, 'Student login successful.')
                        return redirect('homepage')
                    else:
                        messages.info(request, 'Student login successful. Waiting for approval.')
                        return redirect('login_view')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    # Provide the form to the template context
    return render(request, 'login.html', {'form': form})

def student(request):
    return render(request,'student.html')

def student_list(request):
    students = Student.objects.all()
    return render(request, 'staff/student.html', {'students': students})

def student_details(request, student_id):
    student = Student.objects.get(id=student_id)
    return render(request, 'staff/student_details.html', {'student': student})

def folder(request,folderid):
    if request.user.is_authenticated:
        folder_user = Folder.objects.get(id=folderid)
        files = File.objects.filter(folder=folder_user)
        context = {'folderid':folderid,'files':files}
        if request.method == 'POST':
            file_user = request.FILES.get('file')
            file_title = request.POST.get('filetitle')
            fileadd = File.objects.create(filetitle=file_title,file=file_user,folder=folder_user)
        return render(request,'folder.html',context)
    else:
        return redirect('homepage')

def addfolder(request):
   if request.method == 'POST':
       folder_name = request.POST['foldername']
       folder_desc = request.POST['folderdesc']
       folder = Folder.objects.create(foldername=folder_name,folderdesc=folder_desc,folderuser=request.user)
       if folder:
           return redirect("activity")
       else:
            messages.error(request,"Folder Not Created")
            return redirect("activity")

def delete_folder(request, folder_id):
    print("Folder ID:", folder_id)  # Debug statement
    try:
        folder = Folder.objects.get(id=folder_id)
        folder.delete_folder()
        return redirect('activity')
    except Folder.DoesNotExist:
        return JsonResponse({'error': 'Folder does not exist'}, status=404)

def delete_file(request, file_id):
    try:
        file = File.objects.get(id=file_id)
        file.delete_file()
        folder_id = file.folder.id
        return redirect('folder', folderid=folder_id)
    except File.DoesNotExist:
        return JsonResponse({'error': 'File does not exist'}, status=404)
        
class ProfileView(View):
    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
            form = StudentProfileForm(instance=student)
        except Student.DoesNotExist:
            student = Student(user=request.user)
            form = StudentProfileForm()

        profile_link = ProfileVisitLink.objects.filter(user=request.user).last()
        generated_link = profile_link.generated_link if profile_link else None

        return render(request, "profile.html", {'form': form, 'student': student, 'generated_link': generated_link})

    def post(self, request):
        try:
            student = Student.objects.get(user=request.user)
            form = StudentProfileForm(request.POST, request.FILES, instance=student)
        except Student.DoesNotExist:
            student = Student(user=request.user)

        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student.user = request.user
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'profile.html', {'form': form, 'student': student})
        
def get_folder_file_data(request):
    folder_count = Folder.objects.count()
    file_count = File.objects.count()
    return JsonResponse({'folder_count': folder_count, 'file_count': file_count})

def get_folder_data(request):
    folders = Folder.objects.annotate(file_count=Count('file'))
    folder_names = [folder.foldername for folder in folders]
    file_counts = [folder.file_count for folder in folders]
    return JsonResponse({'folder_names': folder_names, 'file_counts': file_counts})
    
def profile_visits1(request):
    folders = Folder.objects.annotate(file_count=Count('file'))
    folder_names = [folder.foldername for folder in folders]
    file_counts = [folder.file_count for folder in folders]
    folder_count = Folder.objects.count()
    file_count = File.objects.count()
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
        'user': request.user,
        'folder_names': folder_names, 
        'file_counts': file_counts,
        'folder_count': folder_count, 
        'file_count': file_count
    }
    return render(request,'profile_visits.html',context)

# @login_required
# def generate_visit_link1(request):
#     generated_link = None
#     if request.method == 'POST':
#         generated_link = get_random_string(length=8)
#         ProfileVisitLink.objects.create(user=request.user, generated_link=generated_link)
#         generated_link = request.build_absolute_uri(reverse('profile_visits', kwargs={'generated_link': generated_link}))
#     return render(request, 'generate_link.html', {'generated_link': generated_link})

# def profile_visits2(request, generated_link=None):
#     if generated_link is None:
#         return render(request, 'profile_visits.html') 
#     try:
#         student = Student.objects.get(user=user)
#         folders = Folder.objects.annotate(file_count=Count('file'))
#         file_counts = [folder.file_count for folder in folders]
#         folder_count = Folder.objects.count()
#         file_count = File.objects.count()
#         profile_link = ProfileVisitLink.objects.get(generated_link=generated_link)
#         user = profile_link.user
#         folders = Folder.objects.filter(folderuser=user)
#         files = File.objects.filter(folder__in=folders)
#         folders_with_file_count = Folder.objects.filter(folderuser_id=user_id).annotate(num_files=Count('file'))
#         folder_names = [folder.foldername for folder in folders] 
        
#         context = {
#         'student': student,
#         'user': request.user,
#         'folder_names': folder_names, 
#         'file_counts': file_counts,
#         'folder_count': folder_count, 
#         'file_count': file_count,
#         'folders_with_file_count': folders_with_file_count,
#         }
#         return render(request, 'profile_visits.html', context)
#     except ProfileVisitLink.DoesNotExist:
#         pass
#     return render(request, 'profile_visits_not_found.html')

# @login_required
# def generate_visit_link1(request):
#     if request.method == 'POST':
#         generated_link = str(uuid.uuid4())[:8] 
#         ProfileVisitLink.objects.create(user=request.user, generated_link=generated_link)

#         qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
#         qr.add_data(request.build_absolute_uri(reverse('profile_visits', kwargs={'generated_link': generated_link})))
#         qr.make(fit=True)
#         qr_img = qr.make_image(fill_color="black", back_color="white")
#         qr_img_buffer = BytesIO()
#         qr_img.save(qr_img_buffer, format='PNG')
#         response = HttpResponse(qr_img_buffer.getvalue(), content_type='image/png')
#         response['Content-Disposition'] = 'attachment; filename="profile_visit_qr.png"'
#         return response
#     else:
#         generated_link = ProfileVisitLink.objects.filter(user=request.user).last().generated_link
#         return render(request, 'generate_link.html', {'generated_link': generated_link})

# @login_required
# def generate_visit_link2(request):
#     if request.method == 'POST':
#         generated_link = str(uuid.uuid4())[:8] 
#         ProfileVisitLink.objects.create(user=request.user, generated_link=generated_link)

#         qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
#         qr.add_data(request.build_absolute_uri(reverse('profile_visits', kwargs={'generated_link': generated_link})))
#         qr.make(fit=True)
#         qr_img = qr.make_image(fill_color="black", back_color="white")
#         qr_img_buffer = BytesIO()
#         qr_img.save(qr_img_buffer, format='PNG')
#         response = HttpResponse(qr_img_buffer.getvalue(), content_type='image/png')
#         response['Content-Disposition'] = 'attachment; filename="profile_visit_qr.png"'
#         return response
#     else:
#         profile_visit_link = ProfileVisitLink.objects.filter(user=request.user).last()
#         if profile_visit_link:
#             generated_link = profile_visit_link.generated_link
#         else:
#             generated_link = None
#         return render(request, 'generate_link.html', {'generated_link': generated_link})

def generate_qr_code(request, generated_link):
    full_link = request.build_absolute_uri(reverse('profile_visits', kwargs={'generated_link': generated_link}))
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

def logout_view(request):
    logout(request)
    return redirect('login_view')

def generate_visit_link(request):
    try:
        student = request.user.student  # Retrieve the student object associated with the user
    except Student.DoesNotExist:
        student = None

    if request.method == 'POST':
        generated_link = str(uuid.uuid4())[:8] 
        ProfileVisitLink.objects.create(user=request.user, generated_link=generated_link)

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(request.build_absolute_uri(reverse('profile_visits', kwargs={'generated_link': generated_link})))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img_buffer = BytesIO()
        qr_img.save(qr_img_buffer, format='PNG')
        response = HttpResponse(qr_img_buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="profile_visit_qr.png"'
        return response
    else:
        profile_visit_link = ProfileVisitLink.objects.filter(user=request.user).last()
        if profile_visit_link:
            generated_link = profile_visit_link.generated_link
            student = request.user.student
        else:
            generated_link = None
            student =None
        return render(request, 'generate_link.html', {'generated_link': generated_link, 'student':student})

def generate_qr_code1(request, generated_link):
    # Construct the full URL for the generated link
    full_link = request.build_absolute_uri(reverse('profile_visits', kwargs={'generated_link': generated_link}))

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_link)
    qr.make(fit=True)

    # Generate the QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Load the logo image
    logo_path = os.path.join(settings.STATIC_ROOT, 'assets/img/logo1.jpg')
    logo_img = Image.open(logo_path)

    # Calculate the position to center the logo
    qr_width, qr_height = qr_img.size
    logo_width, logo_height = logo_img.size
    position = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)

    # Paste the logo onto the QR code image
    qr_img.paste(logo_img, position)

    # Prepare the HTTP response with the QR code image
    response = HttpResponse(content_type="image/png")
    qr_img.save(response, "PNG")
    return response

def profile_visits(request, generated_link=None):
    if generated_link is None:
        return render(request, 'profile_visits.html') 
    try:
        profile_link = ProfileVisitLink.objects.get(generated_link=generated_link)
        user = profile_link.user
        student = Student.objects.get(user=user)
        folders_with_file_count = Folder.objects.filter(folderuser=user).annotate(num_files=Count('file'))
        folder_names = [folder.foldername for folder in folders_with_file_count] 
        file_counts = [folder.num_files for folder in folders_with_file_count]
        folder_count = Folder.objects.filter(folderuser=user).count()
        file_count = File.objects.filter(folder__folderuser=user).count()

        context = {
            'student': student,
            'user': user,
            'folder_names': folder_names, 
            'file_counts': file_counts,
            'folder_count': folder_count, 
            'file_count': file_count,
            'folders_with_file_count': folders_with_file_count,
        }
        return render(request, 'profile_visits.html', context)
    except ProfileVisitLink.DoesNotExist:
        pass
    return render(request, 'profile_visits_not_found.html')