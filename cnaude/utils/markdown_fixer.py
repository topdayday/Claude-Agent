import markdown
import re
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
class MarkdownFixer:
    """
    专门用于修复从大模型（如Gemini、ChatGPT等）返回的Markdown内容
    主要解决代码块缩进问题和格式化问题
    """
    
    def __init__(self):
        self.md = md = markdown.Markdown(extensions=[
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
    
    def fix_code_blocks(self, content: str) -> str:
        """
        修复代码块缩进问题
        """
        lines = content.split('\n')
        fixed_lines = []
        in_code_block = False
        code_block_indent = 0
        
        for line in lines:
            # 检测代码块开始
            if '```' in line and not in_code_block:
                # 找到代码块开始，记录其缩进级别
                code_block_indent = len(line) - len(line.lstrip())
                in_code_block = True
                # 移除代码块标记前的缩进
                fixed_lines.append(line.lstrip())
            elif '```' in line and in_code_block:
                # 代码块结束
                in_code_block = False
                # 移除代码块结束标记前的缩进
                fixed_lines.append(line.lstrip())
            elif in_code_block:
                # 在代码块内部，保持代码的相对缩进，但移除外层缩进
                if len(line) >= code_block_indent:
                    fixed_lines.append(line[code_block_indent:])
                else:
                    fixed_lines.append(line.lstrip())
            else:
                # 普通文本行，保持原样
                fixed_lines.append(line)
        
        result = '\n'.join(fixed_lines)
        return result
    
    def fix_list_formatting(self, content: str) -> str:
        """
        修复列表格式问题，确保代码块与列表项之间有适当的空行
        """
        # 在列表项和代码块之间添加空行
        pattern = r'(\d+\.\s+.*?)\n(\s*```)'
        content = re.sub(pattern, r'\1\n\n\2', content, flags=re.MULTILINE)
        
        # 在代码块结束和下一个内容之间添加空行
        pattern = r'(```\s*)\n([^\n\s])'
        content = re.sub(pattern, r'\1\n\n\2', content, flags=re.MULTILINE)
        
        return content
    
    def remove_excessive_indentation(self, content: str) -> str:
        """
        使用正则表达式移除过度缩进
        """
        # 移除列表项后代码块前的多余缩进
        pattern = r'(\d+\.\s+.*?\n)(\s{4,})(```)'
        result = re.sub(pattern, r'\1\3', content, flags=re.MULTILINE | re.DOTALL)
        return result
    
    def normalize_content(self, content: str) -> str:
        """
        标准化内容格式
        """
        # 移除行尾空格
        if not content:
            return ''
        
        lines = [line.rstrip() for line in content.split('\n')]
        
        # 移除多余的空行（超过2个连续空行的情况）
        normalized_lines = []
        empty_line_count = 0
        
        for line in lines:
            if line.strip() == '':
                empty_line_count += 1
                if empty_line_count <= 2:  # 最多保留2个连续空行
                    normalized_lines.append(line)
            else:
                empty_line_count = 0
                normalized_lines.append(line)
        
        result = '\n'.join(normalized_lines)
        return result
    
    def fix_all(self, content: str) -> str:
        """
        应用所有修复方法
        """
        # 按顺序应用各种修复
        content = self.normalize_content(content)
        content = self.remove_excessive_indentation(content)
        content = self.fix_code_blocks(content)
        content = self.fix_list_formatting(content)
        
        return content
    
    def convert_to_html(self, content: str, auto_fix: bool = True) -> str:
        """
        将Markdown转换为HTML
        
        Args:
            content: Markdown内容
            auto_fix: 是否自动修复格式问题
        
        Returns:
            HTML字符串
        """
        if not content:
            return ""
        if auto_fix:
            content = self.fix_all(content)
        
        return self.md.convert(content)
    