from cnaude.llm.Claude2 import start_conversation_claude2, translate_conversation_his_v2
from cnaude.llm.Claude3 import start_conversation_claude3, start_conversation_claude3_with_documents, translate_conversation_his_v3
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
from cnaude.llm.PalmyraX5 import start_conversation_palmyra_x5, translate_conversation_his_palmyra
from cnaude.llm.GptOss import start_conversation_gptoss, translate_conversation_his_gptoss
from cnaude.utils.JwtTool import obtain_jwt_token, protected_view, generate_api_token
from cnaude.utils.Captcha import captcha_base64
# from cnaude.utils.markdown_fixer import MarkdownFixer
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import markdown
import hashlib
from django.views.decorators.http import require_http_methods
from cnaude.model.Models import Conversation, Member, Captcha, Attachment, ConversationSerializer, MemberSerializer, AttachmentSerializer
from datetime import datetime, timedelta
import logging
import os,json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import mimetypes
from urllib.parse import quote

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

session_count_cache = {}

# md = markdown.Markdown(extensions=[
#     'markdown.extensions.fenced_code',
#     'markdown.extensions.codehilite',
#     'markdown.extensions.abbr',
#     'markdown.extensions.admonition',
#     'markdown.extensions.attr_list',
#     'markdown.extensions.def_list',
#     'markdown.extensions.footnotes',
#     'markdown.extensions.meta',
#     'markdown.extensions.nl2br',
#     'markdown.extensions.tables',
#     'markdown.extensions.toc',
#     'markdown.extensions.wikilinks',
#     'markdown.extensions.sane_lists',
#     'markdown.extensions.smarty',
# ], extension_configs={
#     'markdown.extensions.codehilite': {
#         'css_class': 'highlight',
#         'use_pygments': True,
#         'noclasses': True,
#         'linenums': False,
#         'guess_lang': True,
#         'pygments_style': 'monokai'
#     }
# })
# mdTools = MarkdownFixer()

def get_md5(string):
    md5 = hashlib.md5()
    md5.update(string.encode())
    return md5.hexdigest()


def get_token_info(request):
    token = request.POST.get('token')
    token_info = protected_view(token)
    return token_info


def check_daily_usage_limit(member_id):
    """Check if user has exceeded daily usage limit"""
    midnight_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    count = Conversation.objects.filter(member_id=member_id, create_time__gte=midnight_datetime).count()
    if count > 10:
        m_count = Member.objects.filter(id=member_id, vip_level__gt=0).count()
        if m_count == 0:
            return False
    return True


def get_conversation_history(session_id):
    """Get conversation history for a session"""
    return Conversation.objects.filter(session_id=session_id, del_flag=False)[:5]


def process_llm_request(model_type, content_in, session_id, uploaded_files=None):
    """Process LLM request based on model type"""
    m_type = str(model_type)
    records = get_conversation_history(session_id)
    content_out = None
    reason_out = None
    
    if m_type == '50':  # DeepSeek
        previous_content_in = translate_conversation_his_deep_seek(records)
        if len(previous_content_in) > 0:
            content_out, reason_out = start_conversation_deep_seek_chat(content_in, previous_content_in)
        else:
            content_out, reason_out = start_conversation_deepseek(content_in)
            
    elif m_type == '40':  # OpenAI/Qwen
        previous_content_in = translate_conversation_his_openai(records)
        content_out = start_conversation_openai(content_in, previous_content_in, 1)
        
    elif m_type == '1':  # Claude
        previous_content_in = translate_conversation_his_v3(records)
        if uploaded_files:
            content_out = start_conversation_claude3_with_documents(
                input_content=content_in if content_in else None,
                input_files=uploaded_files,
                previous_chat_history=previous_content_in
            )
        else:
            content_out = start_conversation_claude3(content_in, previous_content_in)
            
    elif m_type == '2':  # Gemini
        previous_content_in = translate_conversation_his_gemini(records)
        if uploaded_files:
            file_paths = [f['path'] for f in uploaded_files]
            content_out = start_conversation_gemini(
                content_in if content_in else "请分析这些文件",
                previous_content_in,
                file_paths=file_paths
            )
        else:
            content_out = start_conversation_gemini(content_in, previous_content_in)
            
    elif m_type == '20':  # GenAI Studio
        previous_content_in = translate_conversation_his_genai(records)
        content_out = start_conversation_genai(content_in, previous_content_in)
        
    elif m_type == '10':  # Llama
        previous_content_in = translate_conversation_his_llama(records)
        content_out = start_conversation_llama(content_in, previous_content_in)
        
    elif m_type == '60':  # PalmyraX5
        previous_content_in = translate_conversation_his_palmyra(records)
        content_out = start_conversation_palmyra_x5(content_in, previous_content_in)
        
    elif m_type == '70':  # GPT-OSS 120B
        previous_content_in = translate_conversation_his_gptoss(records)
        content_out = start_conversation_gptoss(content_in, previous_content_in, 0)
        
    else:
        return None, None, 'Invalid model type'
    
    return content_out, reason_out, None


def save_conversation_record(member_id, session_id, content_in, content_out, reason_out, model_type):
    """Save conversation record to database"""
    display_content = content_in.replace('\n', '<br>') if content_in else '[附件]'
    session_count = session_count_cache.get(session_id, 0)
    title_flag = False
    if session_count < 1 and Conversation.objects.filter(session_id=session_id).count() == 0:
        title_flag = True
        
    record = Conversation(
        member_id=member_id,
        session_id=session_id,
        content_in=display_content,
        content_out=content_out,
        reason_out=reason_out,
        model_type=model_type,
        title_flag=title_flag,
        create_time=datetime.now()
    )
    record.save()
    session_count_cache[session_id] = 1
    return record


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
    
    # Check daily usage limit
    if not check_daily_usage_limit(member_id):
        return JsonResponse({'code': 1, 'data': 'The maximum usage is 10 requests per day'})
    
    if not content_in or not session_id:
        return JsonResponse({'code': 1, 'data': 'Missing required parameters'})
    
    # Process LLM request
    content_out, reason_out, error = process_llm_request(model_type, content_in, session_id)
    
    if error:
        return JsonResponse({'code': 1, 'data': error})
    
    if not content_out and not reason_out:
        return JsonResponse({'code': 1, 'data': 'The service is busy. Please try again'})
    
    # Save conversation record
    record = save_conversation_record(member_id, session_id, content_in, content_out, reason_out, model_type)
    
    attachments = Attachment.objects.filter(conversation_id__in=[record.id])
    attachments_serializer = AttachmentSerializer(attachments, many=True)
    attachments_json = attachments_serializer.data   
    
    conversations_serializer = ConversationSerializer(record, many=False)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json,'attachments':attachments_json})


def save_uploaded_file(uploaded_file, member_id):
    """Save uploaded file and return file info"""
    # Generate unique filename
    file_extension = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create directory structure: media/uploads/member_id/yyyymmdd/
    from datetime import datetime
    date_str = datetime.now().strftime('%Y%m%d')
    upload_path = f"uploads/{member_id}/{date_str}/"
    
    # Save file
    file_path = default_storage.save(
        os.path.join(upload_path, unique_filename),
        ContentFile(uploaded_file.read())
    )
    
    # Get file info
    file_info = {
        'original_name': uploaded_file.name,
        'saved_path': os.path.join(default_storage.location, file_path),
        'relative_path': file_path,
        'size': uploaded_file.size,
        'content_type': uploaded_file.content_type or 'application/octet-stream'
    }
    
    return file_info


def determine_file_type(content_type, filename):
    """Determine if file is image, document, etc."""
    if content_type.startswith('image/'):
        return 'image'
    elif content_type in ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'text/plain', 'text/csv', 'application/json']:
        return 'document'
    else:
        # Check by file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return 'image'
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.csv', '.json']:
            return 'document'
        else:
            return 'document'  # Default to document


def process_file_attachments(request, member_id):
    """Process file attachments from request - 支持多种文件字段格式"""
    uploaded_files = []
    attachment_records = []
    
    # 遍历所有文件字段，支持多种命名方式
    for key in request.FILES:
        # 获取该字段的所有文件（支持多文件上传）
        file_list = request.FILES.getlist(key)
        
        for uploaded_file in file_list:
            try:
                # Save file
                file_info = save_uploaded_file(uploaded_file, member_id)
                
                # Determine file type
                file_type = determine_file_type(file_info['content_type'], file_info['original_name'])
                
                uploaded_files.append({
                    'path': file_info['saved_path'],
                    'type': file_type
                })
                
                # Prepare attachment record (will save after conversation is created)
                attachment_records.append({
                    'file_name': file_info['original_name'],
                    'file_path': file_info['relative_path'],
                    'file_type': file_type,
                    'file_size': file_info['size'],
                    'mime_type': file_info['content_type']
                })
                
                logger.info(f"Successfully processed file: {file_info['original_name']} for member {member_id}")
                
            except Exception as e:
                logger.error(f"Error processing file {uploaded_file.name}: {str(e)}")
                # 继续处理其他文件，不因单个文件失败而中断
                continue
    
    logger.info(f"Processed {len(uploaded_files)} files for member {member_id}")
    return uploaded_files, attachment_records


def save_attachment_records(conversation_id, attachment_records):
    """Save attachment records to database"""
    for attachment_data in attachment_records:
        attachment = Attachment(
            conversation_id=conversation_id,
            file_name=attachment_data['file_name'],
            file_path=attachment_data['file_path'],
            file_type=attachment_data['file_type'],
            file_size=attachment_data['file_size'],
            mime_type=attachment_data['mime_type'],
            create_time=datetime.now()
        )
        attachment.save()


@csrf_exempt
@require_http_methods(["POST"])
def assistant_with_attachments(request):
    """Handle assistant requests with file attachments"""
    token_info = get_token_info(request)
    if not token_info:
        return JsonResponse({'code': -1, 'data': 'Token verification failed'})
    
    member_id = token_info['id']
    content_in = request.POST.get('content', '').strip()
    session_id = request.POST.get('session_id')
    model_type = request.POST.get('model_type')
    
    if not session_id or not model_type:
        return JsonResponse({'code': 1, 'data': 'Missing required parameters'})
    
    # Check daily usage limit
    if not check_daily_usage_limit(member_id):
        return JsonResponse({'code': 1, 'data': 'The maximum usage is 10 requests per day'})
    
    try:
        # Process file attachments
        uploaded_files, attachment_records = process_file_attachments(request, member_id)
        
        # Ensure we have either content or attachments
        if not content_in and not uploaded_files:
            return JsonResponse({'code': 1, 'data': 'No content or attachments provided'})
        
        # Process LLM request with attachments
        content_out, reason_out, error = process_llm_request(model_type, content_in, session_id, uploaded_files)
        
        if error:
            return JsonResponse({'code': 1, 'data': error})
        
        if not content_out and not reason_out:
            return JsonResponse({'code': 1, 'data': 'The service is busy. Please try again'})
        
        # Save conversation record
        conversation = save_conversation_record(member_id, session_id, content_in, content_out, reason_out, model_type)
        
        # Save attachment records
        save_attachment_records(conversation.id, attachment_records)
        
        # Return response
        conversations_serializer = ConversationSerializer(conversation, many=False)
        conversations_json = conversations_serializer.data
        
        
        attachments = Attachment.objects.filter(conversation_id__in=[conversation.id])
        attachments_serializer = AttachmentSerializer(attachments, many=True)
        attachments_json = attachments_serializer.data   
         
        return JsonResponse({'code': 0, 'data': conversations_json,'attachments':attachments_json})
        
    except Exception as e:
        logger.error(f"Error in assistant_with_attachments: {str(e)}")
        return JsonResponse({'code': 1, 'data': f'处理请求时出错: {str(e)}'})


@csrf_exempt
@require_http_methods(["POST"])
def latest_session(request):
    token_info = get_token_info(request)
    page_number = request.POST.get('page_number')
    filter_date = request.POST.get('filter_date')
    if filter_date:
        filter_date += ' 23:59:59'
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return JsonResponse({'code': 1, 'data': 'Invalid date format'})
        
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
    if filter_date:
        records = Conversation.objects.filter(member_id=m_id, del_flag=0, title_flag=True, create_time__lte=filter_date).order_by('-id')[
              page_number * 30:(page_number + 1) * 30]
    else:    
        records = Conversation.objects.filter(member_id=m_id, del_flag=0, title_flag=True).order_by('-id')[
                page_number * 30:(page_number + 1) * 30]
    conversation_ids = []    
    for record in records:
        session_count_cache[record.session_id] = 1
        conversation_ids.append(record.id)
    # attachments = Attachment.objects.filter(conversation_id__in=conversation_ids)
    # attachments_serializer = AttachmentSerializer(attachments, many=True)
    # attachments_json = attachments_serializer.data    
    
    conversations_serializer = ConversationSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json,'attachments':[]})


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
    
    conversation_ids = [record.id for record in records]
    attachments = Attachment.objects.filter(conversation_id__in=conversation_ids)
    
    attachments_serializer = AttachmentSerializer(attachments, many=True)
    attachments_json = attachments_serializer.data
    
    conversations_serializer = ConversationSerializer(records, many=True)
    conversations_json = conversations_serializer.data
    return JsonResponse({'code': 0, 'data': conversations_json, 'attachments':attachments_json})


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
            "modelId": 2,
            "multimodal":1,
            "desc":"综合能力超强",
            "ver":"v2.5-Pro",
        },
        {
            "name": "Claude",
            "modelId": 1,
            "multimodal":1,
            "desc":"编码能力超强",
            "ver":"v4.1",
        },
        {
            "name": "DeepSeek",
            "modelId": 50,
            "multimodal":0,
            "desc":"数学推理超强",
            "ver":"R1",
        },
        {
            "name": "Qwen",
            "modelId": 40,
            "multimodal":0,
            "desc":"中文能力超强",
            "ver":"max-2025",
        },
        {
            "name": "Llama",
            "modelId": 10,
            "multimodal":0,
            "desc":"响应快且精准",
            "ver":"v4-maverick",
        },
        {
            "name": "Palmyra",
            "modelId": 60,
            "multimodal":0,
            "desc":"超长上下文",
            "ver":"X5",
        },
        {
            "name": "GPT-OSS",
            "modelId": 70,
            "multimodal":0,
            "desc":"OpenAI开源",
            "ver":"120B",
        },
        
    ]
    return JsonResponse({'code': 0, 'data': models})


@csrf_exempt
@require_http_methods(["GET"])
def download_attachment(request, attachment_id):
    """根据附件ID下载附件"""
    try:
        # 验证用户token（从GET参数获取）
        token = request.GET.get('token')
        if not token:
            return JsonResponse({'code': -1, 'data': 'Token is required'}, status=401)
        
        token_info = protected_view(token)
        if not token_info:
            return JsonResponse({'code': -1, 'data': 'Token verification failed'}, status=401)
        
        member_id = token_info['id']
        
        # 查找附件记录
        try:
            attachment = Attachment.objects.get(id=attachment_id)
        except Attachment.DoesNotExist:
            return JsonResponse({'code': 1, 'data': 'Attachment not found'}, status=404)
        
        # 验证权限：检查附件是否属于该用户的对话
        conversation = Conversation.objects.filter(
            id=attachment.conversation_id, 
            member_id=member_id,
            del_flag=False
        ).first()
        
        if not conversation:
            return JsonResponse({'code': -1, 'data': 'Access denied'}, status=403)
        
        # 构建文件完整路径
        file_path = os.path.join(default_storage.location, attachment.file_path)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return JsonResponse({'code': 1, 'data': 'File not found on server'}, status=404)
        
        # 获取文件MIME类型
        mime_type = attachment.mime_type or mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # 读取文件内容
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        except IOError:
            return JsonResponse({'code': 1, 'data': 'Error reading file'}, status=500)
        
        # 创建HTTP响应
        response = HttpResponse(file_content, content_type=mime_type)
        
        # 设置文件下载头信息
        # 对文件名进行URL编码以支持中文文件名
        encoded_filename = quote(attachment.file_name.encode('utf-8'))
        response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
        response['Content-Length'] = len(file_content)
        
        # 添加缓存控制头
        response['Cache-Control'] = 'private, max-age=3600'
        
        logger.info(f"User {member_id} downloaded attachment {attachment_id}: {attachment.file_name}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error downloading attachment {attachment_id}: {str(e)}")
        return JsonResponse({'code': 1, 'data': f'Download failed: {str(e)}'}, status=500)
