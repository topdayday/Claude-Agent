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
        db_table = 't_captcha' 
        verbose_name = 'captcha'
        verbose_name_plural = 'captcha'
        app_label = 'captcha'


class Attachment(models.Model):
    id = models.AutoField(primary_key=True)
    conversation_id = models.PositiveIntegerField(null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)  # image, document, etc.
    file_size = models.PositiveIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_attachment'
        verbose_name = 'attachment'
        verbose_name_plural = 'attachments'
        app_label = 'attachment'

    def __str__(self):
        return self.file_name or str(self.id)


class ConversationFav(models.Model):
    id = models.AutoField(primary_key=True)
    member_id = models.IntegerField(null=False)
    session_id = models.CharField(max_length=32, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    create_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_conversation_fav'
        verbose_name = 'conversation_fav'
        verbose_name_plural = 'conversation_fav'
        app_label = 'conversation'

    def __str__(self):
        return self.title or str(self.id)


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id','session_id', 'content_in',  'content_out', 'reason_out',  'member_id',  'model_type', 'create_time')


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'conversation_id', 'file_name', 'file_type', 'file_size', 'mime_type', 'create_time')


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id','login_name', 'mobile',  'email', 'create_time', 'last_login_time')
        
        
class ConversationFavSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationFav
        fields = ('id', 'member_id', 'session_id', 'title', 'create_time')
