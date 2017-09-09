# -*- coding: utf-8 -*-
import time
from django.db.utils import IntegrityError
from django.http import JsonResponse
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import base64


# 添加发布会接口
@csrf_exempt
def add_event(request):
    eid = request.POST.get ('eid', '')  # 发布会 id
    name = request.POST.get ('name', '')  # 发布会标题
    limit = request.POST.get ('limit', '')  # 限制人数
    status = request.POST.get ('status', '')  # 状态
    address = request.POST.get ('address', '')  # 地址
    start_time = request.POST.get ('start_time', '')  # 发布会时间

    # 判断各个字段是否为空
    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse ({'status': 10021, 'message': 'parameter error'})

    # 判断发布会id是否存在
    result = Event.objects.filter (id=eid)
    if result:
        return JsonResponse ({'status': 10022, 'message': 'event id already exists'})

    # 判断发布会name是否存在
    result = Event.objects.filter (name=name)
    if result:
        return JsonResponse ({'status': 10023, 'message': 'event id already exists'})

    # 如果status为空，设置为1
    if status == '':
        status = 1

    # 插入数据
    # Event.objects.create (id=eid, name=name, limit=limit, status=int (status), address=address, start_time=start_time)
    # return JsonResponse ({'status': 200, 'message': 'add event success'})

    # 插入数据
    try:
        Event.objects.create (id=eid, name=name, limit=limit, status=int (status), address=address, start_time=start_time)
    except ValidationError as e:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse ({'status': 10024, 'message': error})
    return JsonResponse ({'status': 200, 'message': 'add event success'})


# 查询发布会接口
@csrf_exempt
def get_event(request):
    eid = request.GET.get ('eid', '')
    name = request.GET.get ("name", "")
    # eid = base64.b64encode(request.GET.get('eid',''))

    if eid == '' and name == '':
        return JsonResponse ({'status': 10022, 'message': 'query result is empty'})
    # id单独查询
    if eid != '':
        event_list = {}
        try:
            result = Event.objects.get (id=eid)
        except ObjectDoesNotExist:
            return JsonResponse ({'status': 10022, 'message': 'query result is empty'})
        else:
            event_list['name'] = result.name
            event_list['limit'] = result.limit
            event_list['address'] = result.address
            event_list['status'] = result.status
            event_list['start_time'] = result.start_time
            return JsonResponse ({'status': 200, 'message': 'success', 'data': event_list})
    # name单独查询
    if name != '':
        datas = []
        results = Event.objects.filter (name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append (event)
                return JsonResponse ({'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse ({'status': 10022, 'message': 'query result is empty'})

    # id和name关联查询
    if name != '' and eid != '':
        event_dates = {}
        try:
            resultants = Event.objects.filter (name=name, id=eid)
        except ObjectDoesNotExist:
            return JsonResponse ({'status': 10022, 'message': 'query result is empty'})
        else:
            event_dates['name'] = resultants.name
            event_dates['limit'] = resultants.limit
            event_dates['address'] = resultants.address
            event_dates['status'] = resultants.status
            event_dates['start_time'] = resultants.start_time
            return JsonResponse ({'status': 200, 'message': 'success', 'data': event_dates})


# 嘉宾添加接口
@csrf_exempt
def add_guest(request):
    eid = request.POST.get ('eid', '')  # 关联发布会 id
    realname = request.POST.get ('realname', '')  # 姓名
    phone = request.POST.get ('phone', '')  # 手机号
    email = request.POST.get ('email', '')  # 邮箱

    # 参数为空判断
    if eid == '' or realname == '' or phone == '':
        return JsonResponse ({'status': 10021, 'message': 'parameter error'})

    # 查询发布会id是否存在
    result = Event.objects.filter (id=eid)
    if not result:
        return JsonResponse ({'status': 10022, 'message': 'event id null'})

    # 判断发布会的状态
    result = Event.objects.get (id=eid).status
    if not result:
        return JsonResponse ({'status': 10023, 'message': 'event status is not available'})

    # 判断发布会的限制人数是否超过
    event_limit = Event.objects.get (id=eid).limit  # 发布会限制人数
    guest_limit = Guest.objects.filter (event_id=eid)  # 发布会已添加的嘉宾数
    # guest_limit = Guest.objects.filter(event_id=eid).count()
    # len人数
    if len (guest_limit) >= event_limit:
        return JsonResponse ({'status': 10024, 'message': 'event number is full'})

    # 验证发布会时间
    event_time = Event.objects.get (id=eid).start_time  # 发布会时间
    timeArray = time.strptime (str (event_time), "%Y-%m-%d %H:%M:%S")
    e_time = int (time.mktime (timeArray))

    now_time = str (time.time ())  # 当前时间
    ntime = now_time.split (".")[0]
    n_time = int (ntime)

    if n_time >= e_time:
        return JsonResponse ({'status': 10025, 'message': 'event has started'})

    try:
        Guest.objects.create (realname=realname, phone=int (phone), email=email, sign=0, event_id=int (eid))
    except IntegrityError:
        return JsonResponse ({'status': 10026, 'message': 'the event guest phone number repeat'})

    return JsonResponse ({'status': 200, 'message': 'add guest success'})


# 嘉宾查询接口
@csrf_exempt
def get_guest(request):
    eid = request.GET.get ("eid", "")  # 关联发布会 id
    phone = request.GET.get ("phone", "")  # 嘉宾手机号

    if eid == '':
        return JsonResponse ({'status': 10021, 'message': 'eid cannot be empty'})

    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter (phone=phone)
        if results:
            for r in results:
                data = {}
                data['realname'] = r.realname
                data['phone'] = r.phone
                data['email'] = r.email
                data['sign'] = r.sign
                datas.append (data)
            return JsonResponse ({'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse ({'status': 10022, 'message': 'query result is empty'})

    if eid != '' and phone != '':
        resultant = {}
        try:
            result = Guest.objects.get (phone=phone, event_id=eid)
        except ObjectDoesNotExist:
            return JsonResponse ({'status': 10022, 'message': 'query result is empty'})
        else:
            resultant['realname'] = result.realname
            resultant['phone'] = result.phone
            resultant['email'] = result.email
            resultant['sign'] = result.sign
            return JsonResponse ({'status': 200, 'message': 'success', 'data': resultant})


# 签到接口
@csrf_exempt
def user_sign(request):
    eid = request.POST.get ('eid', '')
    phone = request.POST.get ('phone', '')

    # 判断是否为空
    if eid == '' or phone == '':
        return JsonResponse ({'status': 10021, 'message': 'parameter error'})

    # 判断发布会id是否存在
    result = Event.objects.filter (id=eid)
    if not result:
        return JsonResponse ({'status': 10022, 'message': 'event id null'})

    # 判断手机号是否存在
    result = Guest.objects.filter (phone=phone)
    if not result:
        return JsonResponse ({'status': 10025, 'message': 'user phone null'})

    # 判断发布会状态
    result = Event.objects.get (id=eid).status
    if not result:
        return JsonResponse ({'status': 10023, 'message': 'event status is not available'})

    # 判断发布会时间与当前时间
    event_time = Event.objects.get (id=eid).start_time  # 发布会时间
    timeArray = time.strptime (str (event_time), "%Y-%m-%d %H:%M:%S")
    e_time = int (time.mktime (timeArray))
    now_time = str (time.time ())  # 当前时间
    ntime = now_time.split (".")[0]
    n_time = int (ntime)

    if n_time >= e_time:
        return JsonResponse ({'status': 10025, 'message': 'event has started'})

    # 判断发布会与嘉宾手机号是否关联
    result = Guest.objects.filter (event_id=eid, phone=phone)
    if not result:
        return JsonResponse ({'status': 10026, 'message': 'user did not participate in the conference'})

    # 判断是否已签到，若没有，则更新签到状态，返回正确结果
    result = Guest.objects.get (event_id=eid, phone=phone).sign
    if result:
        return JsonResponse ({'status': 10027, 'message': 'user has sign in'})
    else:
        Guest.objects.filter (event_id=eid, phone=phone).update (sign='1')
        return JsonResponse ({'status': 200, 'message': 'sign success'})
