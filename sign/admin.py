from django.contrib import admin

# Register your models here.
from sign.models import Guest, Event

# 新建了 EventAdmin 类，继承 django.contrib.admin.ModelAdmin 类，保存着一个类的自定义配置，以供Admin 管理工具使用
class EventAdmin (admin.ModelAdmin):
    list_display = ['name', 'limit', 'status', 'address', 'id', 'create_time']
    # search_fields 用于创建表字段的搜索器，可以设置搜索关键字匹配多个表字段。list_filter 用于创建字段过滤器
    search_fields = ['name']
    list_filter = ['status']


class GuestAdmin (admin.ModelAdmin):
    list_display = ['event', 'realname', 'phone', 'email', 'sign', 'create_time']
    search_fields = ['realname', 'phone']
    list_filter = ['sign']


admin.site.register (Event, EventAdmin)  # 用 EventAdmin 选项注册Event模块
admin.site.register (Guest, GuestAdmin)


