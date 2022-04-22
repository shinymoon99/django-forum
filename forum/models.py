from distutils import version
from django.db import models
from django.contrib.auth.models import User


# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User,
                                verbose_name="关联用户",
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=10, verbose_name="姓名", null=True)
    avatar = models.ImageField(default='default.jpg',
                               upload_to='profile_images')
    status = models.PositiveSmallIntegerField(default=0, verbose_name="vip身份")
    scors = models.IntegerField(verbose_name="积分")

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

    def __str__(self):
        return self.user.username


class Resource(models.Model):
    title = models.CharField(max_length=100, verbose_name="名称")
    description = models.TextField(verbose_name="描述")
    file = models.FileField(upload_to="resource", verbose_name="文件")
    up_dated = models.DateTimeField(auto_now=True, verbose_name="上传时间")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name="提供者")
    status = models.PositiveSmallIntegerField(default=0, verbose_name="是否免费")
    price = models.FloatField(null=True, verbose_name="价格")
    category = models.PositiveSmallIntegerField(default=0, verbose_name="类别")

    class Meta:
        verbose_name = '资源'
        verbose_name_plural = '资源'
        ordering = ["-up_dated"]

    def __repr__(self):
        return (f"title:{self.title}, date:{self.up_dated},"
                f"author: {self.author!r}")


class Comment(models.Model):
    context = models.CharField(max_length=200, verbose_name="内容")
    up_dated = models.DateTimeField(auto_now=True, verbose_name="日期")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    resource = models.ForeignKey(Resource,
                                 on_delete=models.CASCADE,
                                 verbose_name="资源")

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ["-up_dated"]


class Resource_Collector(models.Model):
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE)
    resource_id = models.ForeignKey(to=Resource, on_delete=models.CASCADE)
    date_collect = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '资源收藏'
        verbose_name_plural = '资源收藏'
        ordering = ["-date_collect"]


class Buy(models.Model):
    user_id = models.ForeignKey(to=User, on_delete=models.CASCADE)
    resource_id = models.ForeignKey(to=Resource, on_delete=models.CASCADE)
    buy_dated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '资源购买'
        verbose_name_plural = '资源购买'
        ordering = ["-buy_dated"]


class Question(models.Model):
    title = models.CharField(max_length=100, verbose_name="题目")
    description = models.TextField(verbose_name="内容")
    img = models.ImageField(upload_to="question_img",
                            null=True,
                            verbose_name='图片')
    up_dated = models.DateTimeField(auto_now=True, verbose_name='提交日期')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='提交用户')
    category = models.PositiveSmallIntegerField(default=0, verbose_name='类别')

    class Meta:
        verbose_name = '问答'
        verbose_name_plural = '问答'
        ordering = ["-up_dated"]


class Question_Collector(models.Model):
    user_id = models.ForeignKey(to=User,
                                on_delete=models.CASCADE,
                                verbose_name='用户')
    question_id = models.ForeignKey(to=Question,
                                    on_delete=models.CASCADE,
                                    verbose_name="问题")
    date_collect = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '问答收藏'
        verbose_name_plural = '问答收藏'
        ordering = ["-date_collect"]


# Answer
class Answer(models.Model):
    context = models.CharField(max_length=200, verbose_name="内容")
    up_dated = models.DateTimeField(auto_now=True, verbose_name="日期")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE,
                                 verbose_name="问题")

    class Meta:
        verbose_name = '回答'
        verbose_name_plural = '回答'
        ordering = ["-up_dated"]


class Schedule(models.Model):
    week = models.PositiveSmallIntegerField(verbose_name="周次")
    day = models.PositiveSmallIntegerField(verbose_name="星期")
    one = models.PositiveSmallIntegerField(verbose_name="第几节")
    room = models.CharField(max_length=20, verbose_name="教室")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")

    class Meta:
        verbose_name = '教室使用表'
        verbose_name_plural = '教室使用表'


s_1 = [f'南1_{i}' for i in range(130, 161)]
s_2 = [f'南2_{i}' for i in range(161, 171)]
s_3 = [f'南3_{i}' for i in range(171, 199)]
s_3_ = [f'南3_{i}' for i in range(313, 316)]
s_4 = [f'南4_{i}' for i in range(199, 211)]

n_1 = [f'北1_{i}' for i in range(1, 34)]
n_2 = [f'北2_{i}' for i in list(range(34, 59)) + [39, 40, 2203]]
n_3 = [f'北3_{i}' for i in range(59, 107)]
n_4 = [f'北4_{i}' for i in range(107, 119)]
n_5 = [f'北5_{i}' for i in range(119, 130)]

ALL_ROOMS = s_1 + s_2 + s_3 + s_3_ + s_4 + n_1 + n_2 + n_3 + n_4 + n_5
