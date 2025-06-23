from django.db import models
from rest_framework import serializers


class Conversation(models.Model):
    id = models.AutoField(primary_key=True, )
    member_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    session_id = models.CharField(max_length=255, null=True, blank=True,)
    content_in = models.TextField(blank=True)
    content_out = models.TextField(blank=True)
    reason_out = models.TextField(blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    model_type = models.PositiveSmallIntegerField(default=0)
    del_flag = models.BooleanField(default=False)
    title_flag = models.BooleanField(default=False)


    class Meta:
        app_label = 'conversation'
        db_table = 't_conversation'
        verbose_name = 'conversation'
        verbose_name_plural = 'conversation'

    def __str__(self):
        return str(self.id)


from django.db import models


class Member(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='')
    login_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='')
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name='')
    mobile = models.CharField(max_length=255, null=True, blank=True, verbose_name='')
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name='')
    vip_level = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='')
    last_login_time = models.DateTimeField(null=True, blank=True, verbose_name='')

    class Meta:
        db_table = 't_member'
        verbose_name = 'member'
        verbose_name_plural = 'member'
        app_label = 'member'

    def __str__(self):
        return self.login_name


class Captcha(models.Model):
    id = models.IntegerField(primary_key=True)
    captcha_text = models.CharField(max_length=16)
    create_time = models.DateTimeField()

    class Meta:
        db_table = 't_captcha'  # 指定数据库表名
        verbose_name = 'captcha'
        verbose_name_plural = 'captcha'
        app_label = 'captcha'


class TokenUsage(models.Model):
    id = models.AutoField(primary_key=True)
    member_id = models.PositiveIntegerField()  # 用户ID
    conversation_id = models.PositiveIntegerField(null=True, blank=True)  # 对话ID，关联到Conversation
    session_id = models.CharField(max_length=255, null=True, blank=True)  # 会话ID
    model_type = models.PositiveSmallIntegerField()  # 模型类型
    model_name = models.CharField(max_length=100, null=True, blank=True)  # 模型名称
    input_tokens = models.PositiveIntegerField(default=0)  # 输入token数
    output_tokens = models.PositiveIntegerField(default=0)  # 输出token数
    total_tokens = models.PositiveIntegerField(default=0)  # 总token数
    create_time = models.DateTimeField()  # 创建时间

    class Meta:
        db_table = 't_token_usage'
        verbose_name = 'token_usage'
        verbose_name_plural = 'token_usage'
        app_label = 'token_usage'
        indexes = [
            models.Index(fields=['member_id', 'create_time']),
            models.Index(fields=['member_id', 'model_type']),
        ]

    def __str__(self):
        return f"TokenUsage-{self.id}"


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id','session_id', 'content_in',  'content_out', 'reason_out',  'member_id',  'model_type', 'create_time')


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id','login_name', 'mobile',  'email', 'create_time', 'last_login_time')


class TokenUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenUsage
        fields = ('id', 'member_id', 'conversation_id', 'session_id', 'model_type', 'model_name', 
                  'input_tokens', 'output_tokens', 'total_tokens', 'create_time')
