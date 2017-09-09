from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from sign.models import Event, Guest

# Create your views here.

def index(request):
    # return HttpResponse("Hello Django!")
    return render (request, "index.html")


def qj(request):
    return render (request, "qj.html")


def login_action(request):
    # if request.method == 'get':
    # username = request.get.get ('username', '')
    # password = request.get.get ('password', '')
    # if username == 'admin' and password == '123':
    # # return HttpResponse ('login success')
    # return render (request, 'index.html', {'error': 'login success'})
    # else:
    # return render (request, 'index.html', {'error': '用户名或密码 error!'})
    if request.method == 'GET':
        username = request.GET.get ('username', '')
        password = request.GET.get ('password', '')
        user = auth.authenticate (username=username, password=password)
        if user is not None:
            auth.login (request, user)  # 登陆
            # if username == 'admin' and password == '123':
            # return HttpResponse ('login success')
            # return HttpResponseRedirect ('/event_manage/')
            response = HttpResponseRedirect ('/event_manage/')
            # response.set_cookie ('user', username, 3600)  #添加浏览器cookie
            request.session['user'] = username  # 将 session 信息记录到浏览器
            return response
        else:
            return render (request, 'index.html', {'error': 'username or password error!'})
    else:
        return HttpResponse ('login error')


# 登陆成功页管理
# @login_required  # 限制页面访问
def event_manage(request):
    # 用于查询所有发布会对象（数据）
    event_list = Event.objects.all ()
    # username = request.COOKIES.get ('user', '')  # 读取cookie
    username = request.session.get ('user', '')  # 读取session
    return render (request, 'event_manage.html', {'user': username, 'events': event_list})
    # return render (request, 'event_manage.html')


# 发布会名称搜索
# @login_required
def search_name(request):
    username = request.session.get ('user', '')
    search_name = request.GET.get ('name', '')
    # 若搜索条件为空的话，返回所有数据
    if search_name == '':
        event_lists = Event.objects.all()
        return render (request, 'event_manage.html',{'events':event_lists})
    else:
        # 模糊匹配
        event_list = Event.objects.filter (name__contains=search_name)
        return render (request, 'event_manage.html', {'user': username, 'events': event_list})


# 嘉宾管理
# @login_required
def guest_manage(request):
    username = request.session.get ('user', '')
    guest_list = Guest.objects.all ()
    # 分页，每页3条，把查询出来的所有嘉宾列表 guest_list 放到 Paginator 类中
    paginator = Paginator (guest_list, 5)
    # 通过 GET 请求得到当前要显示第几页的数据
    page = request.GET.get ('page')
    # 获取第 page 页的数据。如果当前没有页数，抛 PageNotAnInteger 异常，返回第一页的数据。如果超出最大页数的范围，抛EmptyPage异常，返回最后一页面的数据
    try:
        contacts = paginator.page (page)
    except PageNotAnInteger:
        contacts = paginator.page (1)
    except EmptyPage:
        contacts = paginator.page (paginator.num_pages)
    return render (request, 'guest_manage.html', {'user': username, 'guests': contacts})


# 嘉宾页面搜索
# @login_required
def guest_search(request):
    username = request.session.get ('user', '')
    guest_search = request.GET.get ('phone', '')
    # if guest_search is None:
    # return render (request, 'guest_manage.html', {'hint': '请输入手机号'})
    guest_list = Guest.objects.filter (phone=guest_search)
    paginator = Paginator (guest_list, 2)
    page = request.GET.get ('page')
    try:
        contacts = paginator.page (page)
    except PageNotAnInteger:
        contacts = paginator.page (1)
    except EmptyPage:
        contacts = paginator.page (paginator.num_pages)
    # contacts = paginator.page (page)
    return render (request, 'guest_manage.html', {'user': username, 'guests': contacts})


# 签到页面
# @login_required
def sign_index(request, event_id):
    event = get_object_or_404 (Event, id=event_id)
    num = Guest.objects.filter (event_id=event_id).count ()
    sign_num = Guest.objects.filter (event_id=event_id, sign=1).count ()
    return render (request, 'sign_index.html', {'event': event, 'num': num, 'sign_num': sign_num})


# 签到动作
@csrf_exempt
# @login_required
def sign_index_action(request, event_id):
    event = get_object_or_404 (Event, id=event_id)
    phone = request.POST.get ('phone', '')
    # 初始查询
    num = Guest.objects.filter (event_id=event_id).count ()
    sign_num = Guest.objects.filter (event_id=event_id, sign=1).count ()
    # 查询手机号是否存在
    result = Guest.objects.filter (phone=phone)
    if not result:
        return render (request, 'sign_index.html', {'event': event, 'hint': '手机号有误！请重新输入', 'num': num, 'sign_num': sign_num})
    # 查询该event和phone是否匹配
    result = Guest.objects.filter (phone=phone, event_id=event_id)
    if not result:
        return render (request, 'sign_index.html', {'event': event, 'hint': '该用户未产于此次发布会！请核实', 'num': num, 'sign_num': sign_num})
    # 查询签到状态
    result = Guest.objects.get (phone=phone, event_id=event_id)
    if result.sign:
        return render (request, 'sign_index.html', {'event': event, 'hint': "用户已签到！", 'num': num, 'sign_num': sign_num})
    else:
        Guest.objects.filter (phone=phone, event_id=event_id).update (sign='1')
        # 更新后查询
        num = Guest.objects.filter (event_id=event_id).count ()
        sign_num = Guest.objects.filter (event_id=event_id, sign=1).count ()
        return render (request, 'sign_index.html', {'event': event, 'hint': '签到成功!', 'guest': result, 'num': num, 'sign_num': sign_num})


# 退出
@login_required
def logout(request):
    auth.logout (request)  # 退出登陆
    response = HttpResponseRedirect ('/index/')
    return response
