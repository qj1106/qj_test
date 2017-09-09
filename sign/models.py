from django.db import models

# Create your models here.

# 默认都会生成自增 id,所有不需要声明id字段
# 发布会表
class Event (models.Model):
    name = models.CharField (max_length=100)  # 标题
    limit = models.IntegerField ()  # 人数
    status = models.BooleanField ()  # 状态
    address = models.CharField (max_length=200)  # 地址
    start_time = models.DateTimeField ('events time')  # 开始时间
    create_time = models.DateTimeField (auto_now=True)  # 创建时间，取当前时间

    # __str__()方法告诉 Python 如何将对象以 str 的方式显示出来。所以，为每个模型类添加了__str__()方法
    def __str__(self):
        return self.name

# 需要指定关联的发布会 id
class Guest (models.Model):
    event = models.ForeignKey (Event)  # 关联Event表id，通过 event_id 关联Event表
    realname = models.CharField (max_length=100)  # 姓名
    phone = models.CharField (max_length=64)  # 手机号码
    email = models.EmailField ()  # 邮箱
    sign = models.BooleanField ()  # 签到
    create_time = models.DateTimeField (auto_now=True)  # 创建时间，取当前时间

    # 通过发布会 id +手机号来做为联合主键
    class Meta:
        unique_together = ("event", "phone")

    def __str__(self):
        return self.realname


