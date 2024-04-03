from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True) 
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    register_number = models.CharField(max_length=20, null=True, blank=True)
    request_approved = models.BooleanField(default=False)  
    request_declined = models.BooleanField(default=False)
    def __str__(self):
        return self.username


class RequestToAdmin(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_sent')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.student.username} at {self.timestamp}"

YEAR_CHOICES = (
    ("I year","I year"),
    ('II year','II year'),
    ('III year','III year'),
    ('IV year','IV year')
) 

Depat_CHOICES=(
    ('Artificial Intelligence & Data Science' , 'Artificial Intelligence & Data Science'),
    ('Computer Science Engineering','Computer Science Engineering'),
    ('Electrical and Electronic Engineering','Electrical and Electronic Engineering'),
    ('Electronics and Communication Engineering','Electronics and Communication Engineering'),
    ('Cyber security','Cyber security'),('Mechanical Engineering','Mechanical Engineering')
)

class Folder(models.Model):
    foldername = models.CharField(max_length=50)
    folderdesc = models.CharField(max_length=255)
    folderuser = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.foldername
    def delete_folder(self):
        self.delete()

class File(models.Model):
    filetitle = models.CharField(max_length=50)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    file = models.FileField(upload_to="Files")
    def __str__(self):
        return self.filetitle
    def delete_file(self):
        self.file.delete()
        self.delete()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    year = models.CharField(choices=YEAR_CHOICES,max_length=50)
    degree_department = models.CharField(choices=Depat_CHOICES,max_length=100)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female')))
    linkedin_link =models.URLField(blank=True)
    github_link = models.URLField(blank=True)
    website_link = models.URLField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    about = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ProfileVisitLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_link = models.CharField(max_length=8, unique=True)  # Assuming the link is a string of 8 characters
    qr_code_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def __str__(self):
        return f"Link for {self.user.username}: {self.generated_link}"
        
class QRCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    qr_code_image = models.ImageField(upload_to='qr_codes/')

    def __str__(self):
        return f"QR Code for {self.url} (User: {self.user.username})"