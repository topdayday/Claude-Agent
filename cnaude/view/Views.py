from cnaude.llm.Claude2 import start_conversation_claude2, translate_conversation_his_v2
from cnaude.llm.Claude3 import start_conversation_claude3, translate_conversation_his_v3
from cnaude.llm.Codey import start_conversation_codey
from cnaude.llm.Gemini import start_conversation_gemini, translate_conversation_his_gemini
from cnaude.llm.GenaiStudio import start_conversation_genai, translate_conversation_his_genai
from cnaude.llm.Llama import start_conversation_llama, translate_conversation_his_llama
from cnaude.llm.Mistral import start_conversation_mistral, translate_conversation_his_mistral
from cnaude.llm.PaLM2 import start_conversation_palm2
from cnaude.llm.Unicorn import start_conversation_unicorn_text
from cnaude.llm.OpenAI import start_conversation_openai
from cnaude.llm.DeepSeek import start_conversation_deepseek
from cnaude.llm.DeepSeekCaht import start_conversation_deep_seek_chat
from cnaude.llm.DeepSeekCaht import translate_conversation_his_deep_seek
from cnaude.llm.OpenAI import translate_conversation_his_openai
from cnaude.utils.JwtTool import obtain_jwt_token, protected_view, generate_api_token
from cnaude.utils.Captcha import captcha_base64
from cnaude.utils.markdown_fixer import MarkdownFixer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import markdown
import hashlib
from django.views.decorators.http import require_http_methods
from cnaude.model.Models import Conversation, Member, Captcha, ConversationSerializer, MemberSerializer, TokenUsage, TokenUsageSerializer
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def save_token_usage(member_id, conversation_id, session_id, model_type, token_usage):
    """保存token使用统计信息到数据库"""
    try:
        token_record = TokenUsage(
            member_id=member_id,
            conversation_id=conversation_id,
            session_id=session_id,
            model_type=model_type,
            model_name=token_usage.get('model_name', ''),
            input_tokens=token_usage.get('input_tokens', 0),
            output_tokens=token_usage.get('output_tokens', 0),
            total_tokens=token_usage.get('total_tokens', 0),
            create_time=datetime.now()
        )
        token_record.save()
        logger.info(f"Token usage saved for member {member_id}: {token_usage}")
    except Exception as e:
        logger.error(f"Failed to save token usage: {e}")


session_count_cache = {}

md = markdown.Markdown(extensions=[
    'markdown.extensions.fenced_code',
    'markdown.extensions.codehilite',
    'markdown.extensions.abbr',
    'markdown.extensions.admonition',
    'markdown.extensions.attr_list',
    'markdown.extensions.def_list',
    'markdown.extensions.footnotes',
    'markdown.extensions.meta',
    'markdown.extensions.nl2br',
    'markdown.extensions.tables',
    'markdown.extensions.toc',
    'markdown.extensions.wikilinks',
    'markdown.extensions.sane_lists',
    'markdown.extensions.smarty',
], extension_configs={
    'markdown.extensions.codehilite': {
        'css_class': 'highlight',
        'use_pygments': True,
        'noclasses': True,
        'linenums': False,
        'guess_lang': True,
        'pygments_style': 'monokai'
    }
})
mdTools = MarkdownFixer()

def get_md5(string):
    md5 = hashlib.md5()
    md5.update(string.encode())
    return md5.hexdigest()


def get_token_info(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    return token_info


@csrf_exempt
@require_http_methods(["POST"])
def assistant(request):
    content_in = request.POST.get('content_in')
    session_id = request.POST.get('session_id')
    model_type = request.POST.get('model_type')
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    member_id = token_info['id']
    midnight_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    count = Conversation.objects.filter(member_id=member_id, create_time__gte=midnight_datetime).count()
    if count > 10:
        m_count = Member.objects.filter(id=member_id, vip_level__gt=0).count()
        if m_count == 0:
            return JsonResponse({'code': 1, 'data': 'The maximum usage is 10 requests per day'})
    m_type = str(model_type)
    if content_in and session_id:
        reason_out = None
        token_usage = None
        
        if m_type == '50':
            records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
            previous_content_in = translate_conversation_his_deep_seek(records)
            if len(previous_content_in) > 0:
                content_out, reason_out, token_usage = start_conversation_deep_seek_chat(content_in, previous_content_in)
            else:
                content_out, reason_out, token_usage = start_conversation_deepseek(content_in)
        elif m_type == '40':
            records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
            previous_content_in = translate_conversation_his_openai(records)
            content_out, token_usage = start_conversation_openai(content_in, previous_content_in, 1)
        elif m_type == '1':
            records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
            previous_content_in = translate_conversation_his_v3(records)
            content_out, token_usage = start_conversation_claude3(content_in, previous_content_in)
        elif m_type == '2':
            records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
            previous_content_in = translate_conversation_his_gemini(records)
            content_out, token_usage = start_conversation_gemini(content_in, previous_content_in)
        elif m_type == '20':
            records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
            previous_content_in = translate_conversation_his_genai(records)
            content_out = start_conversation_genai(content_in, previous_content_in)
            # from cnaude.llm.GenaiStudio import start_conversation_genai, translate_conversation_his_genai
        # elif m_type == '0':
        #     records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
        #     previous_content_in = translate_conversation_his_v2(records)
        #     content_out = start_conversation_claude2(content_in, previous_content_in)    
        # elif m_type == '3':
        #     records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
        #     previous_content_in = translate_conversation_his_mistral(records)
        #     content_out = start_conversation_mistral(content_in, previous_content_in)
        # elif m_type == '4':
        #     records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
        #     previous_content_in = translate_conversation_his_gemini(records)
        #     content_out = start_conversation_palm2(content_in, previous_content_in)
        # elif m_type == '5':
        #     records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
        #     previous_content_in = translate_conversation_his_gemini(records)
        #     content_out = start_conversation_codey(content_in, previous_content_in)
        # elif m_type == '6':
        #     content_out = start_conversation_unicorn_text(content_in, 0)
        elif m_type == '10':
            records = Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]
            previous_content_in = translate_conversation_his_llama(records)
            reason_out = None
            content_out, token_usage = start_conversation_llama(content_in, previous_content_in)
        else:
            return JsonResponse({'code': 1, 'data': 'Invalid parameter'})

        if not content_out and not reason_out:
            return JsonResponse({'code': 1, 'data': 'The service is busy. Please try again'})
        content_in = content_in.replace('\n', '<br>')
        session_count = session_count_cache.get(session_id, 0)
        title_flag = False
        if session_count < 1 and Conversation.objects.filter(session_id=session_id).count() == 0:
            title_flag = True
        record = Conversation(member_id=member_id, session_id=session_id, content_in=content_in,
                              content_out=content_out, reason_out=reason_out, model_type=model_type,
                              title_flag=title_flag, create_time=datetime.now())
        record.save()
        
        # 保存token使用统计
        if token_usage:
            save_token_usage(member_id, record.id, session_id, model_type, token_usage)
        
        session_count_cache[session_id] = 1
        # if record.reason_out:
        #     if record.model_type == 2:
        #         reason_out = mdTools.convert_to_html(record.reason_out, True)
        #     else:
        #         reason_out = md.convert(record.reason_out)
        #     record.reason_out = reason_out
        # if record.content_out:
        #     if record.model_type == 2:
        #         content_out = mdTools.convert_to_html(record.content_out, True)
        #     else:
        #         content_out = md.convert(record.content_out)
        #     record.content_out = content_out
        conversations_serializer = ConversationSerializer(record, many=False)
        conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def latest_session(request):
    token_info = get_token_info(request)
    page_number = request.POST.get('page_number')
    if not page_number:
        page_number = 0
    try:
        page_number = int(page_number)
    except BaseException as be:
        print(be.args)
        return JsonResponse({'code': 1, 'data': 'Invalid parameter'})
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    m_id = token_info['id']
    records = Conversation.objects.filter(member_id=m_id, del_flag=0, title_flag=True).order_by('-id')[
              page_number * 30:(page_number + 1) * 30]
    for record in records:
        session_count_cache[record.session_id] = 1
    conversations_serializer = ConversationSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def list_session(request):
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    s_id = request.POST.get('session_id')
    if not s_id:
        return JsonResponse({'code': 1, 'data': 'Invalid session'})
    m_id = token_info['id']
    records = Conversation.objects.filter(member_id=m_id, session_id=s_id, del_flag=0).order_by('id')
    # for record in records:
    #     if record.reason_out:
    #         if record.model_type == 2:
    #             reason_out = mdTools.convert_to_html(record.reason_out, True)
    #         else:
    #             reason_out = md.convert(record.reason_out)
    #         record.reason_out = reason_out
    #     if record.content_out:
    #         if record.model_type == 2:
    #             content_out = mdTools.convert_to_html(record.content_out, True)
    #         else:
    #             content_out = md.convert(record.content_out)
    #         record.content_out = content_out
    conversations_serializer = ConversationSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def del_session(request):
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    s_id = request.POST.get('session_id')
    if not s_id:
        return JsonResponse({'code': 1, 'data': 'Invalid session'})
    m_id = token_info['id']
    Conversation.objects.filter(member_id=m_id, session_id=s_id).update(del_flag=1)
    return JsonResponse({'code': 0, 'data': 'success'})


@csrf_exempt
@require_http_methods(["POST"])
def del_conversation(request):
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    c_id = request.POST.get('c_id')
    if not c_id:
        return JsonResponse({'code': 1, 'data': 'Invalid session'})
    try:
        c_id = int(c_id)
    except BaseException as be:
        print(be.args)
        return JsonResponse({'code': 1, 'data': 'Invalid session'})
    m_id = token_info['id']
    Conversation.objects.filter(member_id=m_id, id=c_id).update(del_flag=1)
    return JsonResponse({'code': 0, 'data': 'success'})


@csrf_exempt
@require_http_methods(["POST"])
def member_info(request):
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    m_id = token_info['id']
    records = Member.objects.filter(id=m_id)
    records.password = '*******'
    records.id = ''
    conversations_serializer = MemberSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def member_edit(request):
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    password = request.POST.get('password')
    if not password:
        return JsonResponse({'code': 1, 'data': 'Password can not be empty'})
    m_id = token_info['id']
    members = Member.objects.filter(id=m_id, password=get_md5(password))
    if not members:
        return JsonResponse({'code': 1, 'data': 'Old password is not correct'})
    mobile = request.POST.get('mobile')
    email = request.POST.get('email')
    members.mobile = mobile
    members.email = email
    new_password = request.POST.get('new_password')
    if new_password:
        md5_pwd = get_md5(new_password)
        Member.objects.filter(id=m_id).update(mobile=mobile, email=email, password=md5_pwd)
    else:
        Member.objects.filter(id=m_id).update(mobile=mobile, email=email)
    members.password = '*******'
    conversations_serializer = MemberSerializer(members, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json})


@csrf_exempt
@require_http_methods(["POST"])
def generate_session(request):
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    session_id = generate_api_token()
    return JsonResponse({'code': 0, 'data': session_id})


@csrf_exempt
@require_http_methods(["POST"])
def get_captcha(request):
    captcha_text, image_base64 = captcha_base64()
    record = Captcha(captcha_text=captcha_text, create_time=datetime.now())
    record.save()
    return JsonResponse({'code': 0, 'data': image_base64})


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    login_name = request.POST.get('login_name')
    password = request.POST.get('password')
    captcha = request.POST.get('captcha')
    if not login_name or not password or not captcha:
        return JsonResponse({'code': 1, 'data': 'Invalid parameter'})
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)
    cc = Captcha.objects.filter(captcha_text=captcha, create_time__gte=one_minute_ago).count()
    if cc == 0:
        return JsonResponse({'code': 1, 'data': 'Verification code is not correct'})
    Captcha.objects.filter(captcha_text=captcha).delete()
    md5_pwd = get_md5(password)
    members = Member.objects.filter(login_name=login_name, password=md5_pwd)
    if members:
        Member.objects.filter(login_name=login_name).update(last_login_time=now)
        token = obtain_jwt_token(members[0])
        session_id = generate_api_token()
        data = {"token": token, "session_id": session_id}
        return JsonResponse({'code': 0, 'data': data})
    else:
        return JsonResponse({'code': 1, 'data': 'User name or password is not correct'})


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    print(request.POST)
    login_name = request.POST.get('login_name')
    password = request.POST.get('password')
    captcha = request.POST.get('captcha')
    invite_code = request.POST.get('invite_code')
    if not login_name or not password or not captcha or not invite_code:
        return JsonResponse({'code': 1, 'data': 'Invalid parameter'})
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=3)
    cc = Captcha.objects.filter(captcha_text=captcha, create_time__gte=one_minute_ago).count()
    if cc == 0:
        return JsonResponse({'code': 1, 'data': 'Verification code is not correct'})
    Captcha.objects.filter(captcha_text=captcha).delete()
    if invite_code != 'top2day' and invite_code != captcha + captcha + captcha:
        return JsonResponse({'code': 1, 'data': 'Invitation code not correct'})
    members = Member.objects.filter(login_name=login_name)
    if members:
        return JsonResponse({'code': 1, 'data': 'The user name already exists. Please change the user name'})
    else:
        md5_pwd = get_md5(password)
        record = Member(login_name=login_name, password=md5_pwd, create_time=datetime.now())
        record.save()
        members_signin = Member.objects.filter(login_name=login_name, password=md5_pwd)
        data = {}
        if members_signin:
            token = obtain_jwt_token(members_signin[0])
            session_id = generate_api_token()
            data = {"token": token, "session_id": session_id}
        return JsonResponse({'code': 0, 'data': data})


@csrf_exempt
@require_http_methods(["POST"])
def list_llm(request):
    models = [
        {
            "name": "Gemini",
            "modelId": 2
        },
        {
            "name": "Claude",
            "modelId": 1
        },
        {
            "name": "DeepSeek",
            "modelId": 50
        },
        {
            "name": "Qwen",
            "modelId": 40
        },
        {
            "name": "Llama",
            "modelId": 10
        },
        
    ]
    return JsonResponse({'code': 0, 'data': models})


@csrf_exempt
@require_http_methods(["POST"])
def token_usage_stats(request):
    """获取用户的token使用统计信息"""
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    
    member_id = token_info['id']
    page_number = request.POST.get('page_number', 0)
    page_size = request.POST.get('page_size', 20)
    
    try:
        page_number = int(page_number)
        page_size = int(page_size)
        if page_size > 100:  # 限制每页最大数量
            page_size = 100
    except ValueError:
        return JsonResponse({'code': 1, 'data': 'Invalid parameter'})
    
    # 获取用户的token使用记录
    records = TokenUsage.objects.filter(member_id=member_id).order_by('-create_time')[
        page_number * page_size:(page_number + 1) * page_size
    ]
    
    token_usage_serializer = TokenUsageSerializer(records, many=True)
    token_usage_json = token_usage_serializer.data
    
    return JsonResponse({'code': 0, 'data': token_usage_json})


@csrf_exempt
@require_http_methods(["POST"])
def token_usage_summary(request):
    """获取用户的token使用汇总统计"""
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    
    member_id = token_info['id']
    start_date = request.POST.get('start_date')  # 格式: YYYY-MM-DD
    end_date = request.POST.get('end_date')      # 格式: YYYY-MM-DD
    
    # 构建查询条件
    query_filter = {'member_id': member_id}
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query_filter['create_time__gte'] = start_datetime
        except ValueError:
            return JsonResponse({'code': 1, 'data': 'Invalid start_date format, use YYYY-MM-DD'})
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query_filter['create_time__lt'] = end_datetime
        except ValueError:
            return JsonResponse({'code': 1, 'data': 'Invalid end_date format, use YYYY-MM-DD'})
    
    # 获取统计数据
    
    # 总体统计
    total_stats = TokenUsage.objects.filter(**query_filter).aggregate(
        total_calls=Count('id'),
        total_input_tokens=Sum('input_tokens'),
        total_output_tokens=Sum('output_tokens'),
        total_tokens=Sum('total_tokens')
    )
    
    # 按模型类型统计
    model_stats = []
    model_types = TokenUsage.objects.filter(**query_filter).values('model_type', 'model_name').distinct()
    
    for model_type in model_types:
        model_usage = TokenUsage.objects.filter(
            **query_filter,
            model_type=model_type['model_type']
        ).aggregate(
            calls=Count('id'),
            input_tokens=Sum('input_tokens'),
            output_tokens=Sum('output_tokens'),
            total_tokens=Sum('total_tokens')
        )
        
        model_stats.append({
            'model_type': model_type['model_type'],
            'model_name': model_type['model_name'],
            'calls': model_usage['calls'] or 0,
            'input_tokens': model_usage['input_tokens'] or 0,
            'output_tokens': model_usage['output_tokens'] or 0,
            'total_tokens': model_usage['total_tokens'] or 0
        })
    
    # 按日期统计（最近7天）
    import pytz
    
    daily_stats = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())
        
        day_usage = TokenUsage.objects.filter(
            member_id=member_id,
            create_time__gte=day_start,
            create_time__lte=day_end
        ).aggregate(
            calls=Count('id'),
            input_tokens=Sum('input_tokens'),
            output_tokens=Sum('output_tokens'),
            total_tokens=Sum('total_tokens')
        )
        
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'calls': day_usage['calls'] or 0,
            'input_tokens': day_usage['input_tokens'] or 0,
            'output_tokens': day_usage['output_tokens'] or 0,
            'total_tokens': day_usage['total_tokens'] or 0
        })
    
    summary_data = {
        'total_stats': {
            'total_calls': total_stats['total_calls'] or 0,
            'total_input_tokens': total_stats['total_input_tokens'] or 0,
            'total_output_tokens': total_stats['total_output_tokens'] or 0,
            'total_tokens': total_stats['total_tokens'] or 0
        },
        'model_stats': model_stats,
        'daily_stats': daily_stats
    }
    
    return JsonResponse({'code': 0, 'data': summary_data})


@csrf_exempt
@require_http_methods(["POST"])
def token_usage_daily(request):
    """获取用户每日token使用统计"""
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    
    member_id = token_info['id']
    days = request.POST.get('days', 30)  # 默认查询最近30天
    
    try:
        days = int(days)
        if days > 365:  # 限制最多查询1年
            days = 365
    except ValueError:
        return JsonResponse({'code': 1, 'data': 'Invalid days parameter'})
    

    
    daily_stats = []
    for i in range(days):
        date = timezone.now().date() - timedelta(days=i)
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())
        
        day_usage = TokenUsage.objects.filter(
            member_id=member_id,
            create_time__gte=day_start,
            create_time__lte=day_end
        ).aggregate(
            calls=Count('id'),
            input_tokens=Sum('input_tokens'),
            output_tokens=Sum('output_tokens'),
            total_tokens=Sum('total_tokens')
        )
        
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'calls': day_usage['calls'] or 0,
            'input_tokens': day_usage['input_tokens'] or 0,
            'output_tokens': day_usage['output_tokens'] or 0,
            'total_tokens': day_usage['total_tokens'] or 0
        })
    
    return JsonResponse({'code': 0, 'data': daily_stats})
