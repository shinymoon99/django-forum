from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import (
    ALL_ROOMS,
    Answer,
    Comment,
    Question_Collector,
    Resource,
    Question,
    Resource_Collector,
    Schedule,
    Buy,
    Profile,
)
from .forms import UserRegisterForm
import pandas as pd
from .recommend import model_establish
from django.core.cache import cache


def search(request):
    context = {}
    if request.method == "POST":
        keyword = request.POST.get('keyword', None)
        if keyword is None:
            messages.error(request, "没有关键词")
            return redirect('index')
        resources = Resource.objects.filter(description__icontains=keyword)
        context['resources'] = resources
        questions = Question.objects.filter(description__icontains=keyword)
        context['questions'] = questions
        context['keyword'] = keyword
        return render(request, "forum/search.html", context)
    return redirect('index')


# 注册界面
def register(request):
    if request.user.is_authenticated:
        return redirect("movie", "all")

    form = UserRegisterForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            user = User.objects.get(username=username)
            Profile.objects.create(user=user, scors=20)

            messages.success(request, f"{username}的账户已经注册成功，请登录使用！")
            return redirect("login")
        else:
            messages.error(request, "账户名或者密码不符合要求, 注册失败！")
    return render(request, "forum/register.html", {'form': form})


def resource(request, cat):
    context = {}
    map_cat = {'exam': 0, 'compete': 1, "research": 2}
    map_title = {'exam': '考试', 'compete': "竞赛", "research": "科研"}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q

    if cat == 'all':
        if cache.get('all_re'):
            resources = cache.get('all_re')
        else:
            resources = Resource.objects.all()
            cache.set('all_re', resources)
        context['resources'] = resources
        context['title'] = "所有"
    else:
        if cache.get(f'{cat}_re'):
            resources = cache.get(f'{cat}_re')
        else:
            cat_id = map_cat.get(cat, 0)
            resources = Resource.objects.filter(category=cat_id)
            cache.set(f'{cat}_re', resources)
        context['resources'] = resources
        context['title'] = map_title.get(cat, "考试")
    return render(request, "forum/resource.html", context)


@login_required
def vip(request):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    profile = Profile.objects.filter(user=request.user)
    if not profile.exists():
        profile = Profile.objects.create(user=request.user,
                                         name=request.user.username,
                                         scors=0)

    if request.method == 'POST':
        profile = request.user.profile
        profile.status = 1
        profile.save()

        messages.success(request, "您成功升级为vip！")
        return redirect('vip')
    return render(request, "forum/vip.html", context)


@login_required
def buy_resource(request, id):
    if cache.get(f'res_{id}'):
        resource = cache.get(f'rec_{id}')
    else:
        resource = get_object_or_404(Resource, id=id)
        cache.set(f'rec_{id}', resource)
    if resource.price > request.user.profile.scors:
        messages.error(request, "积分不够！")
        return redirect('single_resource', id)
    profile = request.user.profile
    profile.scors = profile.scors - resource.price
    profile.save()
    Buy.objects.create(user_id=request.user, resource_id=resource)
    messages.success(request, "购买成功！")
    return redirect('single_resource', id)


def single_resource(request, id):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    profile = Profile.objects.filter(user=request.user)
    if not profile.exists():
        profile = Profile.objects.create(user=request.user,
                                         name=request.user.username,
                                         scors=0)
    if cache.get(f'res_{id}'):
        resource = cache.get(f'rec_{id}')
    else:
        resource = get_object_or_404(Resource, id=id)
        cache.set(f'rec_{id}', resource)

    if request.method == 'POST':
        if 'comment' in request.POST:
            context = request.POST.get('context')
            Comment.objects.create(context=context,
                                   user=request.user,
                                   resource=resource)
            messages.success(request, "评论提交成功！")
            return redirect('single_resource', id)

    if resource.status == 1:
        if request.user.is_authenticated:
            buy = Buy.objects.filter(resource_id=resource,
                                     user_id=request.user)
            if buy.exists():
                context['bought'] = 2
    if request.user.profile.status == 1:
        context['bought'] = 1

    if request.user.is_authenticated:
        if Resource_Collector.objects.filter(user_id=request.user).filter(
                resource_id=resource).exists():
            context['collect'] = 1
    context['resource'] = resource
    return render(request, "forum/single_resource.html", context)


def question(request, cat):
    context = {}
    map_cat = {'exam': 0, 'compete': 1, "research": 2}
    map_title = {'exam': '考试', 'compete': "竞赛", "research": "科研"}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q

    if cat == 'all':
        if cache.get('all_q'):
            questions = cache.get('all_q')
        else:
            questions = Question.objects.all()
            cache.set('all_q', questions)
        context['questions'] = questions
        context['title'] = "所有"
    else:
        if cache.get(f'{cat}_q'):
            questions = cache.get(f'{cat}_q')
        else:
            cat_id = map_cat.get(cat, 0)
            questions = Question.objects.filter(category=cat_id)
            cache.set(f'{cat}_q', questions)
        context['questions'] = questions
        context['title'] = map_title.get(cat, "考试")
    return render(request, "forum/question.html", context)


def single_question(request, id):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    if cache.get(f'q_{id}'):
        question = cache.get(f'q_{id}')
    else:
        question = get_object_or_404(Question, id=id)
        cache.set(f'q_{id}', question)
    if request.method == 'POST':
        context = request.POST.get('context')
        Answer.objects.create(context=context,
                              user=request.user,
                              question=question)
        messages.success(request, "您的回答提交成功！")
        return redirect('single_question', id)
    if request.user.is_authenticated:
        if Question_Collector.objects.filter(user_id=request.user).filter(
                question_id=question).exists():
            context['collect'] = 1
    context['question'] = question
    return render(request, "forum/single_question.html", context)


@login_required
def submit_timetable(request):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    if request.method == 'POST':
        file = request.FILES.get('file', None)
        if file is None:
            messages.error(request, '没有文件！')
        suffix = file.name.split('.')[-1]
        if suffix not in ('csv', 'xlsx'):
            messages.error(request, "文件格式错误!")
            return redirect('submit_timetable')
        if suffix == 'csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        for index, row in df.iterrows():
            for i in range(1, 8):
                if row[i] != '':
                    text = row[i]
                    text = text.split()[-1]
                    if "(" not in text:
                        continue
                    text = text.strip('(').strip(')').strip()
                    if ',' not in text:
                        if text not in ALL_ROOMS:
                            continue
                        for week in range(1, 19):
                            Schedule.objects.create(week=week,
                                                    day=i,
                                                    one=index,
                                                    room=text,
                                                    user=request.user)
                    else:
                        week, classroom = text.split(',')
                        if classroom not in ALL_ROOMS:
                            continue
                        if '-' in week:
                            start, end = week.split('-')
                            start = int(start)
                            end = int(end) + 1
                            for week in range(start, end):
                                Schedule.objects.create(week=week,
                                                        day=i,
                                                        one=index,
                                                        room=text,
                                                        user=request.user)
        messages.success(request, '课程表上传成功！')
        return redirect('submit_timetable')
    return render(request, "forum/submit_timetable.html", context)


@login_required
def check_timetable(request):
    context = {}
    context['weeks'] = list(range(1, 19))
    context['ones'] = list(range(1, 11))
    context['sweek'] = request.session.get('week', 1)
    context['sday'] = request.session.get('day', 1)
    context['sone'] = request.session.get('one', 1)

    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    if request.method == 'POST':
        week = request.POST.get('week')
        day = request.POST.get('day')
        one = request.POST.get('one')
        week = int(week)
        day = int(day)
        one = int(one)
        schedules = Schedule.objects.filter(week=week).filter(day=day).filter(
            one=one).all()
        if len(schedules) > 0:
            userd_rooms = [schedule.room for schedule in schedules]
            avaiable_rooms = [
                room for room in ALL_ROOMS if room not in userd_rooms
            ]
        else:
            avaiable_rooms = ALL_ROOMS
        if len(avaiable_rooms) > 0:
            if len(avaiable_rooms) > 5:
                context['avaiable_rooms'] = avaiable_rooms[:5]
            else:
                context['avaiable_rooms'] = avaiable_rooms
        context['sweek'] = week
        context['sday'] = day
        context['sone'] = one
        request.session['week'] = week
        request.session['day'] = day
        request.session['one'] = one
        context['submit'] = 1
        return render(request, "forum/check_timetable.html", context)

    return render(request, "forum/check_timetable.html", context)


@login_required
def submit_resource(request):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title')
        description = request.POST.get('description')
        if 'status' in request.POST:
            status = 0
            price = None
        else:
            status = 1
            price = request.POST.get('price', None)
        if price is not None:
            try:
                price = float(price)
            except ValueError:
                messages.success(request, '价格数据错误！')
                return redirect('submit_resource')
        category = request.POST.get('category')
        category = int(category)
        file = request.FILES.get('file', None)
        Resource.objects.create(
            title=title,
            description=description,
            file=file,
            status=int(status),
            price=price,
            category=category,
            author=request.user,
        )
        messages.success(request, '资源提交成功！')
        return redirect('submit_resource')

    return render(request, "forum/submit_resource.html", context)


@login_required
def submit_question(request):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    if request.method == 'POST':
        description = request.POST.get('description')
        category = request.POST.get('category')
        category = int(category)
        img = request.FILES.get('file', None)
        if img is not None:
            if img.name.split('.')[-1] not in ("png", "jpg", "jpeg", "gif"):
                messages.error(request, '提交的文件为图片格式！')
            return redirect('submit_question')
        Question.objects.create(
            title=description[:50],
            description=description,
            img=img,
            category=category,
            author=request.user,
        )
        messages.success(request, '问题提交成功！')
        return redirect('submit_question')

    return render(request, "forum/submit_question.html", context)


@login_required
def use_room(request, room):
    week = request.session['week']
    day = request.session['day']
    one = request.session['one']
    Schedule.objects.create(week=week,
                            day=day,
                            one=one,
                            room=room,
                            user=request.user)
    messages.success(request, '空闲教室预定成功!')
    return redirect(check_timetable)


@login_required
def collect_resource(request, id):
    resource = get_object_or_404(Resource, id=id)
    Resource_Collector.objects.create(user_id=request.user,
                                      resource_id=resource)
    messages.success(request, "资源收藏成功！")

    return redirect('single_resource', id)


@login_required
def remove_resource(request, id):
    resource = get_object_or_404(Resource, id=id)
    Resource_Collector.objects.filter(user_id=request.user).filter(
        resource_id=resource).delete()
    messages.success(request, "资源删除收藏成功！")

    return redirect('single_resource', id)


@login_required
def collect_question(request, id):
    question = get_object_or_404(Question, id=id)
    Question_Collector.objects.create(user_id=request.user,
                                      question_id=question)
    messages.success(request, "该问题收藏成功！")
    return redirect('single_question', id)


@login_required
def remove_question(request, id):
    question = get_object_or_404(Question, id=id)
    Question_Collector.objects.filter(user_id=request.user).filter(
        question_id=question).delete()
    messages.success(request, "问题删除收藏成功！")

    return redirect('single_question', id)


def home(request):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    return render(request, "forum/index.html", context)


@login_required
def recommend_resource(request):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    collects = Resource_Collector.objects.all().values('user_id',
                                                       'resource_id')
    df = pd.DataFrame(list(collects))
    if len(df) > 100:
        resource_ids = model_establish(df, request.user.id)
        resources = Resource.objects.filter(id__in=list(resource_ids))
        context['resources'] = resources
    return render(request, "forum/resource_rec.html", context)


@login_required
def recommend_question(request):
    context = {}
    if cache.get('hot_res'):
        context['hot_res'] = cache.get('hot_res')
    else:
        hot_res = Resource.objects.all()[:5]
        cache.set('hot_res', hot_res)
        context['hot_res'] = hot_res
    if cache.get('hot_q'):
        context['hot_q'] = cache.get('hot_q')
    else:
        hot_q = Question.objects.all()[:5]
        cache.set('hot_q', hot_q)
        context['hot_q'] = hot_q
    collects = Question_Collector.objects.all().values('user_id',
                                                       'question_id')
    df = pd.DataFrame(list(collects))
    if len(df) > 100:
        question_ids = model_establish(df, request.user.id)
        questions = Question.objects.filter(id__in=list(question_ids))
        context['questions'] = questions
    return render(request, "forum/question_rec.html", context)
