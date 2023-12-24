from claudecn.utils.Conversation import start_conversation,translate_conversation_his
from claudecn.utils.JwtTool import obtain_jwt_token,protected_view,generate_api_token
from claudecn.utils.CaptchaBase64 import captcha_base64
from django.http import JsonResponse
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import markdown
from claudecn.model.Models import Conversation,Member

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from claudecn.model.Models import Conversation, Member, Captcha, ConversationSerializer, MemberSerializer
from datetime import datetime, timedelta
import secrets
import string
import jwt
import pdb
from django.db.models import Subquery, OuterRef, Min
from django.utils import timezone


md = markdown.Markdown(extensions=[
    'markdown.extensions.fenced_code',
    'markdown.extensions.codehilite'
])


@csrf_exempt
@require_http_methods(["POST"])
def assistant(request):
    content_in = request.POST.get('content_in')
    session_id = request.POST.get('session_id')
    model_type = request.POST.get('model_type')
    token = request.POST.get('token')
    token_info = protected_view(token)
    if not token_info:
        return JsonResponse({'code': 0, 'data': '凭证校验失败，请重新登录！'})
    member_id = token_info['id']
    records = Conversation.objects.filter(session_id=session_id)[:3]
    conversation_his = translate_conversation_his(records)
    if content_in and session_id:
        content_out = start_conversation(content_in, conversation_his, model_type)
        content_in = content_in.replace('\n', '<br>')
        record = Conversation(member_id=member_id, session_id=session_id,content_in=content_in,content_out=content_out,
                              create_time= datetime.now())
        record.save()
        html_out = md.convert(record.content_out)
        record.content_out = html_out
        conversations_serializer = ConversationSerializer(record, many=False)
        conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def latest_session(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    if not token_info:
        return JsonResponse({'code': 1, 'data': '凭证校验失败，请重新登录！'})
    m_id = token_info['id']
    subquery = Conversation.objects.filter(member_id=m_id, del_flag=0).values('session_id').annotate(min_id=Min('id')).values('min_id')
    conversations = Conversation.objects.filter(id__in=Subquery(subquery))
    records = conversations.order_by('-id')[:30]
    conversations_serializer = ConversationSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data':  conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def list_session(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    if not token_info:
        return JsonResponse({'code': 1, 'data': '凭证校验失败，请重新登录！'})
    s_id = request.POST.get('session_id')
    if not s_id:
        return JsonResponse({'code': 1, 'data':  '会话ID不存在！'})
    m_id = token_info['id']
    records = Conversation.objects.filter(member_id=m_id,session_id=s_id, del_flag=0).order_by('id')
    for record in records:
        html_out = md.convert(record.content_out)
        record.content_out = html_out
    conversations_serializer = ConversationSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data':  conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def del_session(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    if not token_info:
        return JsonResponse({'code': 1, 'data': '凭证校验失败，请重新登录！'})
    s_id = request.POST.get('session_id')
    if not s_id:
        return JsonResponse({'code': 1, 'data':  '会话ID不存在！'})
    m_id = token_info['id']
    Conversation.objects.filter(member_id=m_id,session_id=s_id).update(del_flag=1)
    return JsonResponse({'code': 0, 'data':  'success'})


@csrf_exempt
@require_http_methods(["POST"])
def member_info(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    if not token_info:
        return JsonResponse({'code': 1, 'data': '凭证校验失败，请重新登录！'})
    m_id = token_info['id']
    records = Member.objects.filter(id=m_id)
    records.password = '*******'
    records.id = ''
    conversations_serializer = MemberSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data':  conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def member_edit(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    if not token_info:
        return JsonResponse({'code': 1, 'data': '凭证校验失败，请重新登录！'})
    password = request.POST.get('password')
    if not password:
        return JsonResponse({'code': 1, 'data': '旧密码不能为空！'})
    m_id = token_info['id']
    members = Member.objects.filter(id=m_id, password=password)
    if not members:
        return JsonResponse({'code': 1, 'data': '旧密码不正确！'})
    mobile = request.POST.get('mobile')
    email = request.POST.get('email')
    members.mobile = mobile
    members.email = email
    new_password = request.POST.get('new_password')
    if new_password:
        Member.objects.filter(id=m_id).update(mobile=mobile,email=email,password=new_password)
    else:
        Member.objects.filter(id=m_id).update(mobile=mobile, email=email)
    members.password = '*******'
    conversations_serializer = MemberSerializer(members, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data':  conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def generate_session(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    if not token_info:
        return JsonResponse({'code': 1, 'data': '凭证校验失败，请重新登录！'})
    session_id = generate_api_token()
    return JsonResponse({'code': 0, 'data': session_id})


@csrf_exempt
@require_http_methods(["POST"])
def get_captcha(request):
    captcha_text, image_base64 = captcha_base64()
    record = Captcha(captcha_text=captcha_text, create_time=datetime.now())
    record.save()
    return JsonResponse({'code': 0, 'data':  image_base64})


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    login_name = request.POST.get('login_name')
    password = request.POST.get('password')
    captcha = request.POST.get('captcha')
    if not login_name or not password or not captcha:
        return JsonResponse({'code': 1, 'data': '参数不能为空！'})
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)
    cc = Captcha.objects.filter(captcha_text=captcha, create_time__gte=one_minute_ago).count()
    if cc == 0:
        return JsonResponse({'code': 1, 'data': '图片验证码错误！'})
    Captcha.objects.filter(captcha_text=captcha).delete()
    members = Member.objects.filter(login_name=login_name, password=password)
    if members:
        token = obtain_jwt_token(members[0])
        session_id = generate_api_token()
        data ={"token": token, "session_id": session_id}
        return JsonResponse({'code': 0, 'data': data})
    else:
        return JsonResponse({'code': 1, 'data': '用户名或密码不正确！'})


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    print(request.POST)
    login_name = request.POST.get('login_name')
    password = request.POST.get('password')
    captcha = request.POST.get('captcha')
    invite_code = request.POST.get('invite_code')
    if not login_name or not password or not captcha or not invite_code:
        return JsonResponse({'code': 1, 'data': '注册必填参数不能为空!'})
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)
    cc = Captcha.objects.filter(captcha_text=captcha, create_time__gte=one_minute_ago).count()
    if cc == 0:
        return JsonResponse({'code': 1, 'data': '错误验证码！'})
    Captcha.objects.filter(captcha_text=captcha).delete()
    if invite_code != captcha+captcha+captcha:
        return JsonResponse({'code': 1, 'data': '邀请码不存在！'})
    members = Member.objects.filter(login_name=login_name)
    if members:
        return JsonResponse({'code': 1, 'data': '用户名已存在，请更更换！'})
    else:
        record = Member(login_name=login_name, password=password, create_time= datetime.now())
        record.save()
        return JsonResponse({'code': 0, 'data': '注册成功，请登录！'})
