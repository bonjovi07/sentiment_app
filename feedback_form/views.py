from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import userClass, UserEmployees, UserClients, UserFeedback, Sentiment
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.db.models import Case, When, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.contrib.sessions.backends.cache import SessionStore
from datetime import timedelta
from django.urls import reverse
from pytz import UTC
from datetime import datetime
import base64,random,nltk,os
from django.conf import settings
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
from googletrans import Translator

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return render(request, 'home.html',)
    else:
        return render(request, 'getstart/getstart.html',) 
    
def loginview(request):
    if request.user.is_authenticated:
        return render(request, 'home.html',)
    else:
        return render(request, 'login/login.html')
    
def process(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request,username = username, password = password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect('/home')
        else:
            messages.error(request, "Office deactivated. Please contact support.")
            return redirect('/loginview')
    else:
        messages.error(request, "Login Failed")
        return redirect('/loginview')

    
def processlogout(request):
    logout(request)
    return HttpResponseRedirect("loginview")

def userclass_status_1(user):
    return user.userclass.status == 1
def permission_required_userclass_status_1(view_func):
    decorated_view_func = user_passes_test(userclass_status_1, login_url='/home', redirect_field_name=None)(view_func)
    return decorated_view_func

#ACCOUNT CRUD
@login_required(login_url='/loginview')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def adminhome(request):
    accounts = User.objects.filter(userclass__status = 0).order_by('-is_active','-id')

    paginator = Paginator(accounts, 10)

    page_number = request.GET.get('page')

    accounts = paginator.get_page(page_number)

    return render(request, 'admin/adminhome.html', {'accounts':accounts})

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def accountsearch(request):
    term = request.GET.get('search','')
    active_status = request.GET.get('category','')
    accounts = User.objects.filter(Q(username__icontains=term) | Q(username__icontains=term, userclass__status=0)).order_by('-id', '-is_active')

    if active_status == 'True':
        accounts = accounts.filter(is_active=True)
    elif active_status == 'False':
        accounts = accounts.filter(is_active=False)

    paginator = Paginator(accounts,10)
    page_number = request.GET.get('page')
    accounts = paginator.get_page(page_number)

    return render(request, 'admin/adminhome.html', {'accounts':accounts})

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def adminAddAcc(request):
    return render(request, 'admin/admin_addacc.html')

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def add_acc(request):
    user_name = request.POST.get('username')
    password = request.POST.get('password')
    conf_password = request.POST.get('password2')
    user_email = request.POST.get('email')
    user_status = request.POST.get('status')
    name = request.POST.get('name')
    try:
        user = User.objects.filter(username=user_name)
        email = User.objects.filter(email=user_email)
        firstname = User.objects.filter(first_name=name)
    except:
        email,user,name = None

    if user or email or firstname:
        return render(request, 'admin/admin_addacc.html',{
            'error_message': "Email or Username or Name is already existing"
         })
    else:
        if(password != conf_password):
            return render(request, 'admin/admin_addacc.html',{
            'error_message': "Password is not the same"
         })
        else:
            user = User.objects.create_user(username=user_name, email=user_email,first_name=name, password=conf_password)
            user.save()
            userclass = userClass.objects.create(status=user_status, user = user)
            userclass.save()
            return HttpResponseRedirect('/adminhome')

# @login_required(login_url='/loginview')
# @permission_required_userclass_status_1
# def delete_acc(request, user_id):
#     User.objects.filter(id = user_id).delete()
#     return HttpResponseRedirect('/adminhome')

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def deactivate_acc (request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return HttpResponseRedirect('/adminhome')

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def activate_acc(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return HttpResponseRedirect('/adminhome')

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def edit_acc(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("Profile does not exist")
    return render(request, 'admin/admin_editacc.html', {'accounts':user})

@login_required(login_url='/loginview')
@permission_required_userclass_status_1
def process_acc_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        conf_password = request.POST.get('password2')
        user_email = request.POST.get('email')
        user_status = request.POST.get('status')
        name = request.POST.get('name')

        try:
            existing_name = User.objects.exclude(id=user_id).filter(first_name=name)
            existing_user = User.objects.exclude(id=user_id).filter(username=user_name)
            existing_email = User.objects.exclude(id=user_id).filter(email=user_email)
        except:
            existing_email, existing_user, existing_name = None

        if existing_user or existing_email or existing_name:
            return render(request, 'admin/admin_editacc.html', {
                'accounts': user,
                'error_message': "Email or Username or Name is already existing"
            })
        else:
            if password != conf_password:
                return render(request, 'admin/admin_editacc.html', {
                    'accounts': user,
                    'error_message': "Password is not the same"
                })
            else:
                user.username = user_name
                user.email = user_email
                user.first_name = name

                if password:
                    user.set_password(password)

                user.save()

                userclass = userClass.objects.get(user=user)
                userclass.status = user_status
                userclass.save()

                return HttpResponseRedirect('/adminhome')
    else:
        try:
            users = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404("Profile does not exist")
        return render(request, 'admin/admin_editacc.html', {'accounts': users})


#USER SETTINGS
@login_required(login_url='/loginview')
def usersettings(request):
    return render(request, 'settings/settingshome.html')

@login_required(login_url='/loginview')
def editusersettings(request):
    return render(request, 'settings/settings.html')

@login_required(login_url='/loginview')
def updateusersettings(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        new_username = request.POST.get('new_username')
        password = request.POST.get('password')
        conf_password = request.POST.get('password2')
        new_name = request.POST.get('new_name')

        try:
            existing_user = User.objects.exclude(id=user_id).filter(username=new_username)
            existing_name = User.objects.exclude(id=user_id).filter(first_name=new_name)
        except:
            existing_user,existing_name= None
        if existing_user or existing_name:
            return render(request, 'settings/settings.html', {
                'error_message': 'Username or Name is already taken'
            })
        else:
            if password != conf_password:
                return render(request, 'settings/settings.html',{
                    'error_message': "Password is not the same"
                })
            else:
                user.username = new_username
                user.first_name = new_name
                if password:
                    user.set_password(password)
                user.save()
                return HttpResponseRedirect('/usersettings')
    else:
        try:
            users = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404("Profile does not exist")
        return render(request, 'settings/settings.html')


#EMPLOYEE CRUD
@login_required(login_url='/loginview')
def employeelist(request):
    if request.user.userclass.status == 1:
        employees = UserEmployees.objects.filter(office_user_id__is_active=True).order_by('-is_active','-date_added')
    else:
        employees = UserEmployees.objects.filter(office_user_id=request.user.id)
    
    users = User.objects.filter(is_active=True)
    paginator = Paginator(employees,10)

    page_number = request.GET.get('page')

    employees = paginator.get_page(page_number)

    employee_obj = {
        'users':users,
        'employees': employees,
    }

    return render(request, 'employees/employees.html', employee_obj)

@login_required(login_url='/loginview')
def employeesearch(request):
    term = request.GET.get('search', '')
    category = request.GET.get('category', '')
    active_status = request.GET.get('active', '')

    if request.user.userclass.status == 1:
        employees = UserEmployees.objects.filter(
            Q(first_name__icontains=term, office_user__is_active=True) |
            Q(last_name__icontains=term, office_user__is_active=True)
        ).order_by('-is_active','-date_added')
    else:
        employees = UserEmployees.objects.filter(
            Q(first_name__icontains=term, office_user=request.user) |
            Q(last_name__icontains=term, office_user=request.user)
        ).order_by('-is_active','-date_added')

    if category:
        try:
            category_id = int(category)
            employees = employees.filter(office_user_id=category_id)
        except ValueError:
            # Handle invalid category value here
            pass

    if active_status:
        if active_status == "True":
            employees = employees.filter(is_active=True)
        elif active_status == "False":
            employees = employees.filter(is_active=False)

    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    employees = paginator.get_page(page_number)

    employee_obj = {
        'employees': employees,
    }
    return render(request, 'employees/employees.html', employee_obj)

@login_required(login_url='/loginview')
def addemployee(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'employees/addemployees.html', {'users':users})

@login_required(login_url='/loginview')
def processaddemployee(request):
    fname = request.POST.get("firstname")
    lname = request.POST.get("lastname")
    pos = request.POST.get("position")
    off = request.POST.get("office")
    officeID = request.POST.get("acc_id")

    if officeID:
        create_office = UserEmployees.objects.create(first_name = fname, last_name=lname, position = pos,office = off,office_user_id=officeID) 
        create_office.save()
        return HttpResponseRedirect('/employeelist')
    else:
        return render(request,'employees/addemployees.html',{
            'error_message': "Error in creating an account"
        })

# @login_required(login_url='/loginview')
# def delete_employee(request, employee_id):
#     UserEmployees.objects.filter(id = employee_id).delete()
#     return HttpResponseRedirect('/employeelist')

def deactivate_employee (request, employee_id):
    employee = UserEmployees.objects.get(id = employee_id)
    employee.is_active = False
    employee.save()
    return HttpResponseRedirect('/employeelist')

def activate_employee (request, employee_id):
    employee = UserEmployees.objects.get(id = employee_id)
    employee.is_active = True
    employee.save()
    return HttpResponseRedirect('/employeelist')


@login_required(login_url='/loginview')
def edit_employee(request, employee_id):
    try:
        employee = UserEmployees.objects.get(pk=employee_id)
        users = User.objects.filter(is_active=True)
    except employee.DoesNotExist:
        raise Http404("Profile does not exist")
    return render(request, 'employees/editemployees.html', {'employee':employee, 'users':users})

@login_required(login_url='/loginview')
def process_edit_employee(request, employee_id):
    employee = get_object_or_404(UserEmployees, id=employee_id)

    if(request.method) == 'POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        pos = request.POST.get("position")
        off = request.POST.get("office")
        officeID = request.POST.get('acc_id')

        employee.first_name = fname
        employee.last_name = lname
        employee.position = pos
        employee.office = off
        employee.office_user_id = officeID
        
        if officeID:
            employee.save()
        else:
            employee.save()
    return HttpResponseRedirect('/employeelist')


#CLIENT-FEEDBACK
@login_required(login_url='/loginview')
def generate_feedbackhome(request):
    return render(request, 'feedback/generate_link.html')

@login_required(login_url='/loginview')
def generate_client(request):
    employees = UserEmployees.objects.filter(office_user_id=request.user.id,is_active = True)
    return render(request, 'feedback/Client-Form.html', {'employees':employees})

@login_required(login_url='/loginview')
def client_process(request):
    name = request.POST.get("name")
    agency = request.POST.get("gency")
    email = request.POST.get("email")
    staff = request.POST.get("staff")
    pov = request.POST.get("pov")

    if agency:
        agency = request.POST.get("gency")
    else:
        agency = "N/A"

    expiration_time_token = timezone.now() + timedelta(minutes=10)
    token = default_token_generator.make_token(request.user)
    base_url = request.build_absolute_uri('/')  # Replace with your base URL

    client_query = UserClients(client_name = name, client_agency=agency, client_token_link=token, client_email = email, purpose_of_visit = pov, expiration_time = expiration_time_token, attending_staff_id = staff )
    client_query.save()

    encoded_id = base64.b64encode(str(client_query.id).encode()).decode()
    link = f"{base_url}client_feedback/{token}/{encoded_id}/"

    staffquery = UserEmployees.objects.filter(id=staff)
    staff = staffquery.first()  # Get the first staff object from the queryset

    context = {
        'link': link,
        'expiration_time': expiration_time_token,
        'client': client_query,
        'staff': staff,
    }

    return render(request, 'feedback/token_link.html', context)

@login_required(login_url='/loginview')
def client_feedback(request, token, encrypt):
    token_link = get_object_or_404(UserClients, client_token_link=token)

    client_id = base64.b64decode(encrypt.encode()).decode()
    client = UserClients.objects.filter(id=client_id).first()

    if client.is_completed:
        return HttpResponseRedirect('/thankyou')

    expiration_time = token_link.expiration_time
    current_time = timezone.now()

    if current_time > expiration_time:
        return HttpResponse("Link has expired.")
    else:
        user = default_token_generator.check_token(request.user, token)
        return render(request, 'feedback/client_feedback.html', {'user': user, 'client':client})
    
@login_required(login_url='/loginview')
def thankyou(request):
    return render(request, 'feedback/thankyou.html')


def analyze_sentiment(user_input):
    dataset_file = "D:/wamp64/www/feedback/sentiment_app/static/dataset.txt"

    def append_to_dataset(text, sentiment):
        with open(dataset_file, "a") as file:
            file.write(f"{text}\t{sentiment}\n")

    dataset = []
    with open(dataset_file, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                text, sentiment = line.split("\t")
                dataset.append((text, sentiment))

    # Getting Stopwords
    stop_words = set(stopwords.words("english"))

    def preprocess_text(text):
        tokens = word_tokenize(text.lower())
        # Remove stop words
        tokens = [token for token in tokens if token not in stop_words]
        return dict([(token, True) for token in tokens])

    # Process the dataset
    preprocessed_dataset = [(preprocess_text(text), sentiment) for (text, sentiment) in dataset]

    # Shuffle the dataset
    random.shuffle(preprocessed_dataset)

    # Spliting dataset into training and testing sets
    train_set = preprocessed_dataset[:int(len(preprocessed_dataset) * 0.8)]
    test_set = preprocessed_dataset[int(len(preprocessed_dataset) * 0.8):]

    # Train the Naive Bayes
    classifier = NaiveBayesClassifier.train(train_set)


    def translate_tagalog_to_english(text):
        translator = Translator(service_urls=['translate.google.com'])
        translation = translator.translate(text, dest='en')
        return translation.text
    
    user_input = translate_tagalog_to_english(user_input)
    preprocessed_input = preprocess_text(user_input)
    sentiment = classifier.classify(preprocessed_input)

    # Get probabilities for each sentiment class
    probabilities = classifier.prob_classify(preprocessed_input)
    negative_prob = probabilities.prob('negative')
    positive_prob = probabilities.prob('positive')
    neutral_prob = probabilities.prob('neutral')

    # Append user input and sentiment to the dataset
    append_to_dataset(user_input, sentiment)

    return {
        'input': user_input,
        'sentiment': sentiment,
        'negative_prob': negative_prob,
        'positive_prob': positive_prob,
        'neutral_prob': neutral_prob,
    }

@login_required(login_url='/loginview')
def process_feedback(request):
    courtesy = request.POST.get('courtesy')
    quality = request.POST.get('quality')
    timeliness = request.POST.get('timeliness')
    efficiency = request.POST.get('efficiency')
    cleanliness = request.POST.get('cleanliness')
    comfort = request.POST.get('comfort')
    comments = request.POST.get('comments')
    client = request.POST.get('client_id')

    feedback_query = UserFeedback(feedback_courtesy = courtesy, feedback_quality = quality, feedback_timeless = timeliness, feedback_efficiency = efficiency, feedback_cleanliness = cleanliness, feedback_comfort = comfort, feedback_comments = comments, feedback_client_id=client, feedback_user_id = request.user.id)
    feedback_query.save()

    result = analyze_sentiment(comments)

    sentiment_query = Sentiment(sentiment_analysis = result['sentiment'],negative_prob=result['negative_prob'],positive_prob=result['positive_prob'], neutral_prob =result['neutral_prob'], sentiment_feedback_id = feedback_query.id)
    sentiment_query.save()

    client = get_object_or_404(UserClients, id=client)
    client.is_completed = True
    client.save()
    # Redirect to the thank you page

    return HttpResponseRedirect('/thankyou')

@login_required(login_url='/loginview')
def reportshome(request):
    UserClients.objects.filter(Q(is_completed=False)).delete()

    if request.user.userclass.status == 1:
        user_count = User.objects.filter(is_active=True).count()
        client_count = UserClients.objects.count()
        feedbacks = UserFeedback.objects.all()
    else:
        user_count = User.objects.count()
        client_count = UserClients.objects.filter(attending_staff_id__office_user_id=request.user.id).count()
        feedbacks = UserFeedback.objects.filter(feedback_user_id = request.user.id)

    feedback_average = 0.00
    for feedback in feedbacks:
        rating = (feedback.feedback_courtesy + feedback.feedback_quality + feedback.feedback_timeless + feedback.feedback_efficiency + feedback.feedback_comfort + feedback.feedback_cleanliness)/6
        feedback_average += rating

    if feedbacks.count()>0:
        if request.user.userclass.status == 1:
            feedback_average = feedback_average/UserFeedback.objects.count()
        else:
            feedback_average = feedback_average/UserFeedback.objects.filter(feedback_user_id = request.user.id).count()
    else:
        feedback_average = 0.00
        
    feedback_average = format(feedback_average, '.2f')
    obj = {
        "user_count":user_count,
        "client_count":client_count,
        "feedback_average":feedback_average,
    }

    return render(request, 'reports/reportshome.html',{"obj":obj})

@login_required(login_url='/loginview')
def report_offices(request):
    users = User.objects.all().order_by('-is_active','-last_login' )

    paginator = Paginator(users, 10)

    page_number = request.GET.get('page')

    users = paginator.get_page(page_number)

    return render(request, "reports/reports_offices.html",{"users":users})


@login_required(login_url='/loginview')
def report_offices_search(request):
    term = request.GET.get('search','')
    active_status = request.GET.get('category','')

    users = User.objects.filter(Q(first_name__icontains=term) | Q(first_name__icontains=term)).order_by('-is_active','-last_login')

    if active_status == 'True':
        users = users.filter(is_active=True)
    elif active_status == 'False':
        users = users.filter(is_active=False)

    paginator = Paginator(users, 10)

    page_number = request.GET.get('page')

    users = paginator.get_page(page_number)

    return render(request, "reports/reports_offices.html",{"users":users})

@login_required(login_url='/loginview')
def reports_officesummary(request, user_id):
    office = User.objects.get(id=user_id)
    employees = UserEmployees.objects.filter(office_user_id=office.id).values_list('id', flat=True)
    clients = UserClients.objects.filter(attending_staff_id__in=employees)
    client_count = UserClients.objects.filter(attending_staff_id__in=employees).count()

    feedback_average = 0.00
    feedbacks = UserFeedback.objects.filter(feedback_user_id = user_id)

    if feedbacks.count()>0:
        for feedback in feedbacks:
            rating = (feedback.feedback_courtesy + feedback.feedback_quality + feedback.feedback_timeless + feedback.feedback_efficiency + feedback.feedback_comfort + feedback.feedback_cleanliness)/6
            feedback_average += rating
        feedback_average = feedback_average/UserFeedback.objects.filter(feedback_user_id = user_id).count()
    feedback_average = format(feedback_average, '.2f')

    return render(request, 'reports/reports_officesummary.html',{
        "office":office,
        "client_count":client_count,
        "feedback_average":feedback_average,
        })

@login_required(login_url='/loginview')
def reports_feedbacks(request,user_id):
    office = User.objects.get(id = user_id)
    employees = UserEmployees.objects.filter(office_user_id=office.id).values_list('id', flat=True)
    clients = UserClients.objects.filter(attending_staff_id__in=employees).order_by('-client_visit_date')


    for client in clients:
        feedback = client.userfeedback_set.first()
        if feedback:
            rating = (feedback.feedback_courtesy + feedback.feedback_quality + feedback.feedback_timeless + feedback.feedback_efficiency + feedback.feedback_comfort + feedback.feedback_cleanliness)/6
            rating= format(rating, '.2f')

            sentiment = feedback.sentiment_set.first()
            client.sentiment = sentiment.sentiment_analysis
            client.rating = rating
        else:
            client.sentiment = None


    paginator = Paginator(clients, 10)

    page_number = request.GET.get('page')

    clients = paginator.get_page(page_number)

    return render(request, 'reports/reports_feedbacks.html',{
        "office":office,
        "clients":clients,
        })

@login_required(login_url='/loginview')
def reports_feedbacks_search(request, user_id):
    term = request.GET.get('search', '')
    category = request.GET.get('category', '')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    office = User.objects.get(id=user_id)
    employees = UserEmployees.objects.filter(office_user_id=office.id).values_list('id', flat=True)
    clients = UserClients.objects.filter(
        Q(client_name__icontains=term, attending_staff_id__in=employees) |
        Q(client_agency__icontains=term, attending_staff_id__in=employees)
    ).order_by('-client_visit_date')

    if category:
        clients = clients.filter(userfeedback__sentiment__sentiment_analysis=category)

    if date_from:
        date_from = datetime.strptime(date_from, "%Y-%m-%d").date()

    if date_to:
        date_to = datetime.strptime(date_to, "%Y-%m-%d").date()

    if date_from and date_to:
        clients = clients.filter(client_visit_date__range=(date_from, date_to))
    elif date_from:
        clients = clients.filter(client_visit_date__gte=date_from)
    elif date_to:
        clients = clients.filter(client_visit_date__lte=date_to)

    for client in clients:
        feedback = client.userfeedback_set.first()
        if feedback:
            rating = (feedback.feedback_courtesy + feedback.feedback_quality +
                      feedback.feedback_timeless + feedback.feedback_efficiency +
                      feedback.feedback_comfort + feedback.feedback_cleanliness) / 6
            rating = format(rating, '.2f')

            sentiment = feedback.sentiment_set.first()
            client.sentiment = sentiment.sentiment_analysis
            client.rating = rating
        else:
            client.sentiment = None

    paginator = Paginator(clients, 10)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)

    return render(request, 'reports/reports_feedbacks.html', {
        "office": office,
        "clients": clients,
    })


@login_required(login_url='/loginview')
def reports_single(request,user_id,client_id):
        office = User.objects.get(id = user_id)
        client = get_object_or_404(UserClients, id=client_id)
        feedback = UserFeedback.objects.get(feedback_client_id = client_id)

        rating = (feedback.feedback_courtesy + feedback.feedback_quality + feedback.feedback_timeless + feedback.feedback_efficiency + feedback.feedback_comfort + feedback.feedback_cleanliness)/6
        rating= format(rating, '.2f')
        sentiment = Sentiment.objects.get(sentiment_feedback_id = feedback.id)

        return render(request, 'reports/reports_single.html',{
            "office":office,
            "client":client,
            "feedback":feedback,
            "rating":rating,
            "sentiment":sentiment,
        })

@login_required(login_url='/loginview')
def reports_viewreports(request,user_id):
    office = User.objects.get(id = user_id)
    feedbacks = UserFeedback.objects.filter(feedback_user_id = office.id)

    courtesy_counts = {}
    courtesy_rating = 0.00
    quality_counts = {}
    quality_rating = 0.00
    timeless_counts = {}
    timeless_rating = 0.00
    efficiency_counts = {}
    efficiency_rating = 0.00
    cleanliness_counts = {}
    cleanliness_rating = 0.00
    comfort_counts = {}
    comfort_rating = 0.00

    if feedbacks:
        for feedback in feedbacks:
            if feedback.feedback_courtesy in courtesy_counts:
                courtesy_counts[feedback.feedback_courtesy] += 1
            else:
                courtesy_counts[feedback.feedback_courtesy] = 1
            courtesy_rating += feedback.feedback_courtesy

            if feedback.feedback_quality in quality_counts:
                quality_counts[feedback.feedback_quality] += 1
            else:
                quality_counts[feedback.feedback_quality] = 1
            quality_rating += feedback.feedback_quality

            if feedback.feedback_timeless in timeless_counts:
                timeless_counts[feedback.feedback_timeless] += 1
            else:
                timeless_counts[feedback.feedback_timeless] = 1
            timeless_rating += feedback.feedback_timeless

            if feedback.feedback_efficiency in efficiency_counts:
                efficiency_counts[feedback.feedback_efficiency] += 1
            else:
                efficiency_counts[feedback.feedback_efficiency] = 1
            efficiency_rating += feedback.feedback_efficiency

            if feedback.feedback_cleanliness in cleanliness_counts:
                cleanliness_counts[feedback.feedback_cleanliness] += 1
            else:
                cleanliness_counts[feedback.feedback_cleanliness] = 1
            cleanliness_rating += feedback.feedback_cleanliness

            if feedback.feedback_comfort in comfort_counts:
                comfort_counts[feedback.feedback_comfort] += 1
            else:
                comfort_counts[feedback.feedback_comfort] = 1
            comfort_rating += feedback.feedback_comfort

        total_feedbacks = len(feedbacks)
        courtesy_rating = courtesy_rating / total_feedbacks
        quality_rating = quality_rating / total_feedbacks
        timeless_rating = timeless_rating / total_feedbacks
        efficiency_rating = efficiency_rating / total_feedbacks
        cleanliness_rating = cleanliness_rating / total_feedbacks
        comfort_rating = comfort_rating / total_feedbacks

    else:
        total_feedbacks = 0

    feedback_average = 0.00
    if total_feedbacks > 0:
        for feedback in feedbacks:
            rating = (
                feedback.feedback_courtesy
                + feedback.feedback_quality
                + feedback.feedback_timeless
                + feedback.feedback_efficiency
                + feedback.feedback_comfort
                + feedback.feedback_cleanliness
            ) / 6
            feedback_average += rating
        feedback_average = feedback_average / total_feedbacks

    context = {
        "courtesy_counts": courtesy_counts,
        "courtesy_rating": format(courtesy_rating, '.2f'),
        "quality_counts": quality_counts,
        "quality_rating": format(quality_rating, '.2f'),
        "timeless_counts": timeless_counts,
        "timeless_rating": format(timeless_rating, '.2f'),
        "efficiency_counts": efficiency_counts,
        "efficiency_rating": format(efficiency_rating, '.2f'),
        "cleanliness_counts": cleanliness_counts,
        "cleanliness_rating": format(cleanliness_rating, '.2f'),
        "comfort_counts": comfort_counts,
        "comfort_rating": format(comfort_rating, '.2f'),
        "office": office,
        "feedbacks": feedbacks,
        "feedback_average": format(feedback_average, '.2f'),
        "total_feedbacks": total_feedbacks,
    }

    return render(request, 'reports/reports_viewreports.html', context)

@login_required(login_url='/loginview')
def reports_viewreports_search(request, user_id):
    office = User.objects.get(id=user_id)
    feedbacks = UserFeedback.objects.filter(feedback_user_id=office.id)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        feedbacks = feedbacks.filter(feedback_client__client_visit_date__gte=date_from)

    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        date_to = date_to + timedelta(days=1)
        feedbacks = feedbacks.filter(feedback_client__client_visit_date__lt=date_to)

    courtesy_counts = {}
    courtesy_rating = 0.00
    quality_counts = {}
    quality_rating = 0.00
    timeless_counts = {}
    timeless_rating = 0.00
    efficiency_counts = {}
    efficiency_rating = 0.00
    cleanliness_counts = {}
    cleanliness_rating = 0.00
    comfort_counts = {}
    comfort_rating = 0.00

    if feedbacks:
        for feedback in feedbacks:
            if feedback.feedback_courtesy in courtesy_counts:
                courtesy_counts[feedback.feedback_courtesy] += 1
            else:
                courtesy_counts[feedback.feedback_courtesy] = 1
            courtesy_rating += feedback.feedback_courtesy

            if feedback.feedback_quality in quality_counts:
                quality_counts[feedback.feedback_quality] += 1
            else:
                quality_counts[feedback.feedback_quality] = 1
            quality_rating += feedback.feedback_quality

            if feedback.feedback_timeless in timeless_counts:
                timeless_counts[feedback.feedback_timeless] += 1
            else:
                timeless_counts[feedback.feedback_timeless] = 1
            timeless_rating += feedback.feedback_timeless

            if feedback.feedback_efficiency in efficiency_counts:
                efficiency_counts[feedback.feedback_efficiency] += 1
            else:
                efficiency_counts[feedback.feedback_efficiency] = 1
            efficiency_rating += feedback.feedback_efficiency

            if feedback.feedback_cleanliness in cleanliness_counts:
                cleanliness_counts[feedback.feedback_cleanliness] += 1
            else:
                cleanliness_counts[feedback.feedback_cleanliness] = 1
            cleanliness_rating += feedback.feedback_cleanliness

            if feedback.feedback_comfort in comfort_counts:
                comfort_counts[feedback.feedback_comfort] += 1
            else:
                comfort_counts[feedback.feedback_comfort] = 1
            comfort_rating += feedback.feedback_comfort

        total_feedbacks = len(feedbacks)
        courtesy_rating = courtesy_rating / total_feedbacks
        quality_rating = quality_rating / total_feedbacks
        timeless_rating = timeless_rating / total_feedbacks
        efficiency_rating = efficiency_rating / total_feedbacks
        cleanliness_rating = cleanliness_rating / total_feedbacks
        comfort_rating = comfort_rating / total_feedbacks

    else:
        total_feedbacks = 0

    feedback_average = 0.00
    if total_feedbacks > 0:
        for feedback in feedbacks:
            rating = (
                feedback.feedback_courtesy
                + feedback.feedback_quality
                + feedback.feedback_timeless
                + feedback.feedback_efficiency
                + feedback.feedback_comfort
                + feedback.feedback_cleanliness
            ) / 6
            feedback_average += rating
        feedback_average = feedback_average / total_feedbacks

    context = {
        "courtesy_counts": courtesy_counts,
        "courtesy_rating": format(courtesy_rating, '.2f'),
        "quality_counts": quality_counts,
        "quality_rating": format(quality_rating, '.2f'),
        "timeless_counts": timeless_counts,
        "timeless_rating": format(timeless_rating, '.2f'),
        "efficiency_counts": efficiency_counts,
        "efficiency_rating": format(efficiency_rating, '.2f'),
        "cleanliness_counts": cleanliness_counts,
        "cleanliness_rating": format(cleanliness_rating, '.2f'),
        "comfort_counts": comfort_counts,
        "comfort_rating": format(comfort_rating, '.2f'),
        "office": office,
        "feedbacks": feedbacks,
        "feedback_average": format(feedback_average, '.2f'),
        "total_feedbacks": total_feedbacks,
    }

    return render(request, 'reports/reports_viewreports.html', context)


@login_required(login_url='/loginview')
def reports_staff(request, user_id):
    office = User.objects.get(id = user_id)
    employees = UserEmployees.objects.filter(office_user_id=office.id).annotate(client_count=Count('userclients'))

    for employee in employees:
        feedbacks = UserFeedback.objects.filter(feedback_client_id__attending_staff_id=employee.id)
        rating_sum = 0.0
        feedback_count = feedbacks.count()
    
        for feedback in feedbacks:
            rating_sum += (feedback.feedback_courtesy + feedback.feedback_quality + feedback.feedback_timeless + feedback.feedback_efficiency + feedback.feedback_comfort + feedback.feedback_cleanliness) / 6.0

        if feedback_count > 0:
            employee.feedback_average = rating_sum / feedback_count
            employee.feedback_average = format(employee.feedback_average, '.2f')
        else:
            employee.feedback_average = 0.0

    return render(request, 'reports/reports_staff.html',{
        "office":office,
        "employees":employees,
        })


@login_required(login_url='/loginview')
def reports_staff_search(request, user_id):
    office = User.objects.get(id=user_id)
    employees = UserEmployees.objects.filter(office_user_id=office.id)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    feedbacks = UserFeedback.objects.filter(feedback_client__attending_staff__office_user_id=office.id)

    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        feedbacks = feedbacks.filter(feedback_client__client_visit_date__gte=date_from)

    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        date_to += timedelta(days=1)
        feedbacks = feedbacks.filter(feedback_client__client_visit_date__lt=date_to)

    for employee in employees:
        employee_feedbacks = feedbacks.filter(feedback_client__attending_staff_id=employee.id)
        rating_sum = 0.0
        feedback_count = employee_feedbacks.count()
        employee.client_count = feedback_count

        for feedback in employee_feedbacks:
            rating_sum += (feedback.feedback_courtesy + feedback.feedback_quality + feedback.feedback_timeless + feedback.feedback_efficiency + feedback.feedback_comfort + feedback.feedback_cleanliness) / 6.0

        if feedback_count > 0:
            employee.feedback_average = rating_sum / feedback_count
            employee.feedback_average = format(employee.feedback_average, '.2f')
        else:
            employee.feedback_average = 0.0

    return render(request, 'reports/reports_staff.html', {
        "office": office,
        "employees": employees,
    })
