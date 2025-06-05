from vertexai.generative_models._generative_models import ResponseBlockedError
from vertexai.preview.generative_models import GenerativeModel

# temperature
# 温度取值范围【0-2】
# 温度可以控制词元选择的随机性。较低的温度适合希望获得真实或正确回复的提示，
# 而较高的温度可能会引发更加多样化或意想不到的结果。
# 如果温度为 0，系统始终会选择概率最高的词元。

# max_output_tokens
# 输出词元取值范围
# 输出词元限制决定了一条提示的最大文本输出量。
# 一个词元约为 4 个字符。
models_data = [
   {
        "model_id": "gemini-2.5-pro-preview-05-06",
        "max_output_tokens": 65535,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-2.0-flash-thinking-exp-01-21",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-2.0-flash-001",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.5-flash-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.5-pro-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "2M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.5-pro-preview-0409",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "1M content window",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.0-pro-vision-001",
        "max_output_tokens": 2048,
        "temperature": 1.0,
        "top_p": 1,
        "description": "针对视觉进行了优化,稳定",
        "type": "multiplex",
    },
    {
        "model_id": "gemini-1.0-pro-001",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "性能稳定优化版",
        "type": "text",
    },
    {
        "model_id": "gemini-1.0-pro-002",
        "max_output_tokens": 8192,
        "temperature": 1.0,
        "top_p": 1,
        "description": "性能稳定优化版",
        "type": "text",
    },
    {
        "model_id": "gemini-pro",
        "max_output_tokens": 2048,
        "temperature": 1.0,
        "top_p": 1,
        "description": "早期版本",
        "type": "text",
    },
]

def translate_conversation_his_gemini(contents):
    chats_history = []
    for content in contents:
        chat_history = format_chat_history(content.content_in, content.content_out)
        chats_history.extend(chat_history)
    return chats_history

def format_chat_history(content_in, content_out):
    message_in = {"role": "user", "content": content_in}
    message_out = {"role": "model", "content": content_out}
    return [message_in, message_out]

def start_conversation_gemini(content_in, previous_chat_history=[], model_index=0):
    model_data = models_data[model_index]
    config = {
        "max_output_tokens": model_data['max_output_tokens'],
        "temperature":  model_data['temperature'],
        "top_p": model_data['top_p'],
    }
    input_content = []
    output_content = ''
    input_content_obj = {"role": "user", "content": content_in}
    if previous_chat_history:
        input_content.extend(previous_chat_history)
    input_content.append(input_content_obj)
    output_content_str = "\n".join([f"{m['role']}: {m['content']}" for m in input_content])
    model = GenerativeModel(model_data['model_id'])
    chat = model.start_chat()
    try:
        message_out = chat.send_message(output_content_str, generation_config=config)
        output_content = message_out.candidates[0].content.parts[0].text
    except ResponseBlockedError as e:

        print(e.args)
    return output_content


if __name__ == '__main__':
    test = '''
import sys
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QCheckBox, QScrollArea, QPushButton, QSizePolicy
from PySide6.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QGridLayout, QHeaderView, QLabel,
    QLayout, QListView, QMainWindow, QMenuBar,
    QPlainTextEdit, QPushButton, QSizePolicy, QStatusBar,
    QTabWidget, QTableView, QVBoxLayout, QWidget)
from PySide6.QtGui import QColor

class StockTimeAxisItem(pg.AxisItem):
    """自定义股票时间轴，只显示交易时间"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_mapping = {}  # 存储压缩时间戳到原始时间的映射
        
    def setTimeMapping(self, time_mapping):
        """设置时间映射关系"""
        self.time_mapping = time_mapping
        
    def tickStrings(self, values, scale, spacing):
        """自定义时间标签格式"""
        strings = []
        for v in values:
            try:
                # 如果有时间映射，使用映射后的时间
                if self.time_mapping and v in self.time_mapping:
                    original_time = self.time_mapping[v]
                    if isinstance(original_time, pd.Timestamp):
                        time_str = original_time.strftime('%H:%M')
                    else:
                        dt = pd.to_datetime(original_time)
                        time_str = dt.strftime('%H:%M')
                else:
                    # 回退到原始逻辑
                    dt = pd.to_datetime(v, unit='s')
                    time_str = dt.strftime('%H:%M')
                strings.append(time_str)
            except:
                strings.append('')
        return strings
    
    def tickValues(self, minVal, maxVal, size):
        """自定义时间刻度值"""
        try:
            # 如果有时间映射，基于映射的时间范围生成刻度
            if self.time_mapping:
                # 获取在当前范围内的时间戳
                valid_timestamps = [ts for ts in self.time_mapping.keys() 
                                  if minVal <= ts <= maxVal]
                
                if not valid_timestamps:
                    return [([], [])]
                
                # 根据数据点数量决定刻度密度
                num_points = len(valid_timestamps)
                if num_points <= 10:
                    # 数据点少，显示所有点
                    major_ticks = valid_timestamps
                elif num_points <= 50:
                    # 中等数据量，每5个点显示一个刻度
                    step = max(1, num_points // 10)
                    major_ticks = valid_timestamps[::step]
                else:
                    # 数据点多，智能选择刻度
                    step = max(1, num_points // 15)
                    major_ticks = valid_timestamps[::step]
                
                # 确保包含起始和结束点
                if valid_timestamps[0] not in major_ticks:
                    major_ticks.insert(0, valid_timestamps[0])
                if valid_timestamps[-1] not in major_ticks:
                    major_ticks.append(valid_timestamps[-1])
                
                return [(sorted(major_ticks), [])]
            
            # 回退到原始逻辑
            min_dt = pd.to_datetime(minVal, unit='s')
            max_dt = pd.to_datetime(maxVal, unit='s')
            
            time_range = max_dt - min_dt
            
            if time_range.total_seconds() <= 3600:  # 1小时内，每15分钟一个刻度
                freq = '15min'
            elif time_range.total_seconds() <= 7200:  # 2小时内，每30分钟一个刻度
                freq = '30min'
            else:  # 超过2小时，每小时一个刻度
                freq = '1h'
            
            tick_times = pd.date_range(
                start=min_dt.floor('15min'),
                end=max_dt.ceil('15min'),
                freq=freq
            )
            
            major_ticks = [t.timestamp() for t in tick_times]
            major_ticks = [t for t in major_ticks if minVal <= t <= maxVal]
            
            if not major_ticks:
                major_ticks = [minVal, (minVal + maxVal) / 2, maxVal]
            
            return [(major_ticks, [])]
            
        except Exception as e:
            print(f"tickValues error: {e}")
            return super().tickValues(minVal, maxVal, size)

class PercentageAxisItem(pg.AxisItem):
    """自定义百分比Y轴，显示百分比格式"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def tickStrings(self, values, scale, spacing):
        """自定义百分比标签格式"""
        strings = []
        for v in values:
            try:
                # 将数值转换为百分比格式，保留两位小数
                percentage = v * scale
                strings.append(f'{percentage:.2f}%')
            except:
                strings.append('')
        return strings

class MultiLineChart(QWidget):
    def __init__(self, parent=None, data_file=None,data_frame=None,clear_all=True):
        super().__init__(parent)
        self.data_file = data_file
        self.data_frame =data_frame
        if self.data_frame is None:
            self.data_frame = pd.DataFrame(columns=['time', 'volume','preClose', 'gain'])
        # 存储多条线的数据
        self.price_lines = []  # 存储所有价格线条
        self.line_data = []    # 存储每条线的数据
        self.line_names = []   # 存储每条线的名称
        self.line_colors = []  # 存储每条线的颜色
        self.line_visible = [] # 存储每条线的可见性状态
        self.used_colors = set()  # 已使用的颜色
        
        self.initUI()
        self.generateData()
        self.setupChart()
        self.setupInteractions()

        if clear_all:
            self.clearAllLines()

    def initUI(self):
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QScrollArea
        main_layout = QVBoxLayout()
        
        # 创建水平布局，用于图表和左侧区域
        chart_layout = QHBoxLayout()
        
        # 创建图表容器
        chart_container = QWidget()
        chart_container_layout = QVBoxLayout()
        chart_container_layout.setContentsMargins(0, 0, 0, 0)
        chart_container_layout.setSpacing(0)
        
        # 主涨幅图表
        self.price_graph = pg.PlotWidget(axisItems={
            'bottom': StockTimeAxisItem(orientation='bottom'),
            'right': PercentageAxisItem(orientation='right')
        })
        self.price_graph.setBackground('black')
        # self.price_graph.setLabel('left', '涨幅', color='white')
        self.price_graph.showGrid(x=True, y=True, alpha=0.3)
        # 隐藏左侧Y轴，显示右侧Y轴
        self.price_graph.getAxis('left').setStyle(showValues=False)
        self.price_graph.getAxis('right').setPen('white')
        self.price_graph.getAxis('right').setTextPen('white')
        self.price_graph.getAxis('right').setWidth(80)  # 设置右侧Y轴宽度为80
        self.price_graph.getAxis('bottom').setPen('white')
        # 隐藏自动缩放按钮
        self.price_graph.hideButtons()
        # 禁用X、Y轴缩放
        self.price_graph.setMouseEnabled(x=False, y=False)
    
        
        # 成交量图表
        self.volume_graph = pg.PlotWidget(axisItems={
            'bottom': StockTimeAxisItem(orientation='bottom'),
            'right': pg.AxisItem(orientation='right')
        })
        self.volume_graph.setBackground('black')
        # self.volume_graph.setLabel('left', '成交量', color='white')
        self.volume_graph.showGrid(x=True, y=True, alpha=0.3)
        # 隐藏左侧Y轴，显示右侧Y轴
        self.volume_graph.getAxis('left').setStyle(showValues=False)
        self.volume_graph.getAxis('right').setPen('white')
        self.volume_graph.getAxis('right').setTextPen('white')
        self.volume_graph.getAxis('right').setWidth(80)  # 设置右侧Y轴宽度为80
        self.volume_graph.getAxis('bottom').setPen('white')
        # 隐藏自动缩放按钮
        self.volume_graph.hideButtons()
        # 禁用X、Y轴缩放
        self.volume_graph.setMouseEnabled(x=False, y=False)
        
        # 设置图表高度比例
        # self.price_graph.setMinimumHeight(400)
        # self.volume_graph.setMinimumHeight(150)
        
        chart_container_layout.addWidget(self.price_graph, 3)  # 价格图占3/4
        chart_container_layout.addWidget(self.volume_graph, 1)  # 成交量图占1/4
        chart_container.setLayout(chart_container_layout)
        
        # 左侧区域容器（原来的right_container）
        left_container = QWidget()
        left_container.setFixedWidth(160)
        left_container.setStyleSheet("background-color: black;")
        left_container_layout = QVBoxLayout()
        left_container_layout.setContentsMargins(5, 5, 5, 5)
        left_container_layout.setSpacing(5)
        
        # 图例标题
        # legend_title = QLabel("线条图例")
        # legend_title.setStyleSheet("color: white; font-size: 14px; font-weight: bold; padding: 5px;")
        # legend_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # left_container_layout.addWidget(legend_title)
        
        # 添加清除所有按钮
        self.clear_all_btn = QPushButton("清除所有")
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #f44336;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.clear_all_btn.clicked.connect(self.clearAllLines)
        left_container_layout.addWidget(self.clear_all_btn)
        
        # 图例滚动区域
        self.legend_scroll = QScrollArea()
        self.legend_scroll.setWidgetResizable(True)
        self.legend_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid gray;
                background-color: black;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777777;
            }
        """)
        
        # 图例内容容器
        self.legend_widget = QWidget()
        self.legend_layout = QVBoxLayout()
        self.legend_layout.setContentsMargins(5, 5, 5, 5)
        self.legend_layout.setSpacing(0)  # 修改间距为1px
        self.legend_widget.setLayout(self.legend_layout)
        self.legend_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)  # 让内容高度自适应
        self.legend_scroll.setWidget(self.legend_widget)
        
        left_container_layout.addWidget(self.legend_scroll)
        left_container.setLayout(left_container_layout)
        
        chart_layout.addWidget(left_container)
        chart_layout.addWidget(chart_container, 1)
        chart_layout.setSpacing(0)
        main_layout.addLayout(chart_layout)
        self.setLayout(main_layout)

    def generateData(self):
        if self.data_file is None and self.data_frame is None:
            # 如果没有提供数据文件和数据框，初始化空数据
            self._initializeEmptyData()
            return
            
        try:       
            # 从文件读取数据
            if self.data_file is not None: 
                # 读取CSV文件，第一列作为时间列而不是索引
                df = pd.read_csv(self.data_file, index_col=0)
                print(f"过滤前数据量000: {len(df)} 条") 
                # 将索引重置，让时间列成为普通列
                df = df.reset_index()
                # 重命名第一列为time
                df.rename(columns={df.columns[0]: 'time'}, inplace=True)
                
            else:
                df = self.data_frame
            print(f"过滤前数据量111: {len(df)} 条")    
            # 处理时间列 - 确保时间列存在且格式正确
            if 'time' in df.columns:
                # 如果时间列是字符串或数字，尝试解析为datetime
                try:
                    # 先尝试按照预期格式解析
                    df['time'] = pd.to_datetime(df['time'].astype(str), format='%Y%m%d%H%M%S')
                except ValueError:
                    # 如果格式不匹配，尝试自动推断格式
                    try:
                        df['time'] = pd.to_datetime(df['time'])
                    except:
                        print("无法解析时间列，初始化空数据")
                        self._initializeEmptyData()
                        return
            else:
                print("数据中缺少time列，初始化空数据")
                self._initializeEmptyData()
                return
            
            # 检查必要的列是否存在
            required_columns = ['time', 'volume', 'gain']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"缺少必要的列: {missing_columns}，初始化空数据")
                self._initializeEmptyData()
                return
            
            # 过滤只保留交易时间段的数据 (09:30-11:30 和 13:00-15:00)
            df['hour'] = df['time'].dt.hour
            df['minute'] = df['time'].dt.minute
            
            # 创建过滤条件：只保留交易时间段的数据
            # 上午交易时间：09:30-11:30 (包含09:30，不包含11:30)
            # 下午交易时间：13:00-15:00 (包含13:00，包含15:00整点)
            trading_time_filter = (
                # 上午交易时间：09:30-11:29
                (((df['hour'] == 9) & (df['minute'] >= 30)) |
                 (df['hour'] == 10) |
                 ((df['hour'] == 11) & (df['minute'] < 30))) |
                # 下午交易时间：13:00-15:00
                (((df['hour'] == 13)) |
                 (df['hour'] == 14) |
                 ((df['hour'] == 15) & (df['minute'] <= 0)))
            )
            
            # 应用过滤条件
            df_filtered = df[trading_time_filter].copy()
            
            # 删除临时列
            df_filtered = df_filtered.drop(['hour', 'minute'], axis=1)
            
            print(f"过滤前数据量: {len(df)} 条")
            print(f"过滤后数据量: {len(df_filtered)} 条")
            print(f"已过滤为只包含交易时间 (09:30-11:30, 13:00-15:00) 的数据")
            
            # 如果过滤后没有数据，初始化空数据
            if len(df_filtered) == 0:
                print("过滤后没有有效数据，初始化空数据")
                self._initializeEmptyData()
                return
            
            # 按交易日分组处理数据，创建连续的时间序列
            df_filtered['date'] = df_filtered['time'].dt.date
            trading_dates = sorted(df_filtered['date'].unique())
            
            print(f"发现 {len(trading_dates)} 个交易日: {trading_dates}")
            
            # 存储所有处理后的数据
            all_compressed_timestamps = []
            all_volumes = []
            all_gains = []
            all_original_times = []
            time_mapping = {}  # 压缩时间戳到原始时间的映射
            
            # 当前压缩时间的起始点（从0开始，以分钟为单位）
            current_compressed_time = 0
            
            for date_idx, trade_date in enumerate(trading_dates):
                # 获取当天的数据
                day_data = df_filtered[df_filtered['date'] == trade_date].copy()
                
                # 分离上午和下午的数据
                morning_data = day_data[day_data['time'].dt.hour < 12].copy()
                afternoon_data = day_data[day_data['time'].dt.hour >= 13].copy()
                
                print(f"交易日 {trade_date}: 上午 {len(morning_data)} 条, 下午 {len(afternoon_data)} 条")
                
                # 处理上午数据
                if len(morning_data) > 0:
                    # 为上午数据创建连续的压缩时间戳
                    morning_compressed_timestamps = []
                    for i in range(len(morning_data)):
                        compressed_ts = current_compressed_time + i * 60  # 每分钟递增60秒
                        morning_compressed_timestamps.append(compressed_ts)
                        # 建立时间映射
                        time_mapping[compressed_ts] = morning_data.iloc[i]['time']
                    
                    all_compressed_timestamps.extend(morning_compressed_timestamps)
                    all_volumes.extend(morning_data['volume'].values)
                    all_gains.extend(morning_data['gain'].values)
                    all_original_times.extend(morning_data['time'].values)
                    
                    # 更新当前压缩时间点
                    current_compressed_time = morning_compressed_timestamps[-1] + 60
                
                # 处理下午数据
                if len(afternoon_data) > 0:
                    # 为下午数据创建连续的压缩时间戳
                    afternoon_compressed_timestamps = []
                    for i in range(len(afternoon_data)):
                        compressed_ts = current_compressed_time + i * 60  # 每分钟递增60秒
                        afternoon_compressed_timestamps.append(compressed_ts)
                        # 建立时间映射
                        time_mapping[compressed_ts] = afternoon_data.iloc[i]['time']
                    
                    all_compressed_timestamps.extend(afternoon_compressed_timestamps)
                    all_volumes.extend(afternoon_data['volume'].values)
                    all_gains.extend(afternoon_data['gain'].values)
                    all_original_times.extend(afternoon_data['time'].values)
                    
                    # 更新当前压缩时间点，为下一个交易日准备
                    current_compressed_time = afternoon_compressed_timestamps[-1] + 60
            
            # 转换为numpy数组
            self.timestamps = np.array(all_compressed_timestamps)
            self.volumes = np.array(all_volumes)
            gains = np.array(all_gains)
            self.original_times = np.array(all_original_times)
            
            # 设置时间轴的时间映射
            if hasattr(self, 'price_graph') and hasattr(self.price_graph.getAxis('bottom'), 'setTimeMapping'):
                self.price_graph.getAxis('bottom').setTimeMapping(time_mapping)
            if hasattr(self, 'volume_graph') and hasattr(self.volume_graph.getAxis('bottom'), 'setTimeMapping'):
                self.volume_graph.getAxis('bottom').setTimeMapping(time_mapping)
            
            # 检查gain数据的性质
            print(f"gain数据范围: {gains.min():.6f} 到 {gains.max():.6f}")
            
            # 如果gain数据看起来已经是百分比形式的涨幅数据（范围在-1到1之间）
            if gains.min() >= -1 and gains.max() <= 1:
                # 直接使用gain数据作为涨幅百分比
                self.price_changes_pct = gains * 100  # 转换为百分比
                print("使用gain列作为涨幅数据（已转换为百分比）")
            else:
                # 如果gain数据是价格数据，计算涨幅
                if len(gains) > 0 and gains[0] != 0:
                    # 计算相对于第一个价格的涨幅百分比
                    base_price = gains[0]
                    self.price_changes_pct = ((gains - base_price) / base_price) * 100
                    print("计算相对涨幅百分比")
                else:
                    # 如果第一个价格为0或数据为空，使用gain数据本身
                    self.price_changes_pct = gains
                    print("使用gain数据本身作为涨幅")
                
            print(f"成功读取数据: {len(df_filtered)} 条记录")
            print(f"时间范围: {df_filtered['time'].min()} 到 {df_filtered['time'].max()}")
            print(f"压缩后时间戳范围: {self.timestamps.min():.0f} 到 {self.timestamps.max():.0f}")
            print(f"gain范围: {gains.min():.6f} 到 {gains.max():.6f}")
            print(f"涨幅范围: {self.price_changes_pct.min():.2f}% 到 {self.price_changes_pct.max():.2f}%")
            
        except Exception as e:
            print(f"读取数据文件失败: {e}")
            print("初始化空数据")
            self._initializeEmptyData()
    
    def _initializeEmptyData(self):
        """初始化空数据，确保所有必要的属性都存在"""
        self.timestamps = np.array([])
        self.price_changes_pct = np.array([])
        self.volumes = np.array([])
        self.original_times = np.array([])
        print("已初始化空数据")
    
    def _generateSimulatedData(self):
        # 原来的数据生成逻辑
        date_rng = pd.date_range(start='2024-11-22 09:30', end='2024-11-22 15:00', freq='1min')
        
        # 过滤只保留交易时间段的数据 (09:30-11:30 和 13:00-15:00)
        trading_time_filter = (
            # 上午交易时间：09:30-11:29
            (((date_rng.hour == 9) & (date_rng.minute >= 30)) |
             (date_rng.hour == 10) |
             ((date_rng.hour == 11) & (date_rng.minute < 30))) |
            # 下午交易时间：13:00-15:00
            (((date_rng.hour == 13)) |
             (date_rng.hour == 14) |
             ((date_rng.hour == 15) & (date_rng.minute <= 0)))
        )
        
        date_rng_filtered = date_rng[trading_time_filter]
        
        # 保存原始时间戳用于鼠标悬停显示
        self.original_times = date_rng_filtered.copy()
        
        # 创建压缩的时间序列
        morning_data = date_rng_filtered[date_rng_filtered.hour < 12]
        afternoon_data = date_rng_filtered[date_rng_filtered.hour >= 13]
        
        # 创建连续的时间序列
        if len(morning_data) > 0 and len(afternoon_data) > 0:
            # 下午数据的时间戳调整为紧接着上午数据
            last_morning_time = morning_data[-1]
            time_diff = pd.Timedelta(minutes=1)  # 1分钟间隔
            
            # 创建下午的连续时间戳
            afternoon_compressed = []
            for i, _ in enumerate(afternoon_data):
                new_time = last_morning_time + time_diff * (i + 1)
                afternoon_compressed.append(new_time)
            
            # 合并上午和压缩后的下午时间
            compressed_times = list(morning_data) + afternoon_compressed
            compressed_times = pd.DatetimeIndex(compressed_times)
        else:
            compressed_times = date_rng_filtered
        
        self.timestamps = compressed_times.map(pd.Timestamp.timestamp).values
        
        # 生成涨幅走势 - 模拟从0开始的下跌趋势
        n_points = len(date_rng_filtered)
        daily_changes = np.random.normal(-0.01, 0.05, n_points)  # 轻微下跌倾向
        daily_changes[0] = 0  # 开盘时涨幅为0
        
        # 累积涨幅变化
        self.price_changes_pct = np.cumsum(daily_changes)
        
        # 添加一些随机波动
        noise = np.random.normal(0, 0.02, n_points)
        self.price_changes_pct = self.price_changes_pct + noise
        
        # 确保涨幅在合理范围内 (-8% 到 +2%)
        self.price_changes_pct = np.clip(self.price_changes_pct, -8, 2)
        
        # 生成成交量数据
        self.volumes = np.random.exponential(800, n_points)  # 指数分布，平均800
        
        # 在某些时间点增加成交量（模拟交易活跃期）
        active_periods = np.random.choice(n_points, size=n_points//10, replace=False)
        self.volumes[active_periods] *= np.random.uniform(2, 5, len(active_periods))

    
    def clearCharts(self):
        """清空图表中的所有数据项"""
        # 清空价格图表
        self.price_graph.clear()
        
        # 清空成交量图表
        self.volume_graph.clear()
        
        # 隐藏提示标签（但不删除，因为会在setupInteractions中重新使用）
        if hasattr(self, 'label') and self.label is not None:
            self.label.hide()
        
        # 清空图例
        if hasattr(self, 'legend_layout'):
            for i in reversed(range(self.legend_layout.count())):
                item = self.legend_layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                        self.legend_layout.removeItem(item)
        
        # 清空多条线数据
        self.price_lines.clear()
        self.line_data.clear()
        self.line_names.clear()
        self.line_colors.clear()
        self.line_visible.clear()
        self.used_colors.clear()
        
        # 重置数据属性
        if hasattr(self, 'timestamps'):
            del self.timestamps
        if hasattr(self, 'price_changes_pct'):
            del self.price_changes_pct
        if hasattr(self, 'volumes'):
            del self.volumes
        if hasattr(self, 'original_times'):
            del self.original_times

    def addDataFrame(self, data_frame, name):
        """添加新的数据框作为新的线条
        
        Args:
            data_frame: 包含数据的DataFrame
            name: 线条名称，如果为None则自动生成
        """
        if data_frame is None or data_frame is None:
            return
        if len(data_frame)==0   or len(name) == 0:
            return
        if self.line_names.count(name) > 0:
            return       
        # 临时保存当前数据
        old_data_frame = self.data_frame
        
        # 设置新的数据框并生成数据
        self.data_frame = data_frame

        self.generateData()
        
        # 如果成功生成了数据，添加新线条
        if hasattr(self, 'timestamps') and hasattr(self, 'price_changes_pct'):
            # 存储新线条的数据
            line_data = {
                'timestamps': self.timestamps.copy(),
                'price_changes_pct': self.price_changes_pct.copy(),
                'volumes': self.volumes.copy() if hasattr(self, 'volumes') else None,
                'original_times': self.original_times.copy() if hasattr(self, 'original_times') else None
            }
            self.line_data.append(line_data)
            
            # 生成随机颜色
            color = self.getRandomColor()

            line_name = str(name)
          
            # 创建新的线条
            new_line = pg.PlotDataItem(
                x=self.timestamps,
                y=self.price_changes_pct,
                pen=pg.mkPen(color, width=2),
                name=line_name
            )
            
            # 添加到图表
            self.price_graph.addItem(new_line)
            self.price_lines.append(new_line)
            self.line_names.append(line_name)
            self.line_colors.append(color)
            self.line_visible.append(True)  # 新线条默认可见
            
            # 添加对应的成交量柱状图
            if hasattr(self, 'volumes') and len(self.volumes) > 0:
                # 计算柱状图宽度
                if len(self.timestamps) > 1:
                    bar_width = (self.timestamps[1] - self.timestamps[0]) * 0.6  # 减小宽度避免重叠
                else:
                    bar_width = 36  # 默认宽度（减小）
                
                # 为不同数据集添加轻微的X轴偏移，避免完全重叠
                line_index = len(self.line_data) - 1  # 当前线条的索引
                x_offset = (line_index % 3 - 1) * bar_width * 0.2  # 轻微偏移
                
                # 使用与线条相同的颜色，但添加透明度
                base_color = QColor(color)
                base_color.setAlpha(150)  # 设置透明度
                
                # 优化：使用单个BarGraphItem创建所有柱状图，而不是循环创建多个
                x_positions = self.timestamps + x_offset
                heights = self.volumes
                
                # 创建单个柱状图对象包含所有数据
                volume_bars = pg.BarGraphItem(
                    x=x_positions,
                    height=heights,
                    width=bar_width,
                    brush=base_color,
                    pen=pg.mkPen(color, width=1)  # 添加边框
                )
                self.volume_graph.addItem(volume_bars)
                
                # 更新成交量图表范围
                volume_max = self.volumes.max()
                if not np.isnan(volume_max) and volume_max > 0:
                    # 获取当前成交量图表的Y轴范围
                    current_range = self.volume_graph.getViewBox().viewRange()[1]
                    current_max = current_range[1]
                    
                    # 如果新数据的最大成交量超过当前范围，更新范围
                    if volume_max * 1.1 > current_max:
                        self.volume_graph.setYRange(0, volume_max * 1.1)
            
            # 更新图例
            self.updateLegend()
            
            print(f"添加了新线条: {line_name}，颜色: {color}")
        
        # 恢复原始数据框
        self.data_frame = old_data_frame

    def setupChart(self):
        # 检查是否有有效数据
        if not hasattr(self, 'timestamps') or len(self.timestamps) == 0:
            print("没有有效数据，跳过图表设置")
            # 初始化空的主线，避免后续代码出错
            if not self.price_lines:
                # 创建一个空的主线
                self.price_line = pg.PlotDataItem(
                    x=[],
                    y=[],
                    pen=pg.mkPen('white', width=1),
                    name='主线'
                )
                self.price_graph.addItem(self.price_line)
                self.price_lines.append(self.price_line)
                self.line_names.append('主线')
                self.line_colors.append('white')
                self.line_visible.append(True)
                self.used_colors.add('white')
                # 存储空的主线数据
                main_line_data = {
                    'timestamps': np.array([]),
                    'price_changes_pct': np.array([]),
                    'volumes': np.array([]),
                    'original_times': np.array([])
                }
                self.line_data.append(main_line_data)
            
            # 更新图例
            self.updateLegend()
            return
        
        # 绘制涨幅线
        self.price_line = pg.PlotDataItem(
            x=self.timestamps,
            y=self.price_changes_pct,
            pen=pg.mkPen('white', width=1),
            name='主线'
        )
        self.price_graph.addItem(self.price_line)
        
        # 将主线添加到线条列表中（如果还没有添加的话）
        if not self.price_lines:
            self.price_lines.append(self.price_line)
            self.line_names.append('主线')
            self.line_colors.append('white')
            self.line_visible.append(True)
            self.used_colors.add('white')
            # 存储主线数据
            if hasattr(self, 'timestamps') and hasattr(self, 'price_changes_pct'):
                main_line_data = {
                    'timestamps': self.timestamps.copy(),
                    'price_changes_pct': self.price_changes_pct.copy(),
                    'volumes': self.volumes.copy() if hasattr(self, 'volumes') else None,
                    'original_times': self.original_times.copy() if hasattr(self, 'original_times') else None
                }
                self.line_data.append(main_line_data)
        
        # 绘制成交量柱状图
        if len(self.timestamps) > 1:
            bar_width = (self.timestamps[1] - self.timestamps[0]) * 0.8  # 柱状图宽度
        else:
            bar_width = 60  # 默认宽度（1分钟）
        
        # 根据涨跌设置柱状图颜色
        colors = []
        for i, change_pct in enumerate(self.price_changes_pct):
            if i == 0:
                colors.append('gray')
            elif self.price_changes_pct[i] >= self.price_changes_pct[i-1]:
                colors.append('red')  # 上涨用红色
            else:
                colors.append('green')  # 下跌用绿色
        
        # 优化：按颜色分组创建柱状图，减少对象数量
        color_groups = {'gray': [], 'red': [], 'green': []}
        
        for i, (timestamp, volume, color) in enumerate(zip(self.timestamps, self.volumes, colors)):
            color_groups[color].append((timestamp, volume))
        
        # 为每种颜色创建一个BarGraphItem
        for color, data_points in color_groups.items():
            if data_points:  # 如果该颜色有数据点
                x_positions = [point[0] for point in data_points]
                heights = [point[1] for point in data_points]
                
                bars = pg.BarGraphItem(
                    x=x_positions,
                    height=heights,
                    width=bar_width,
                    brush=color,
                    pen=None
                )
                self.volume_graph.addItem(bars)
        
        # 设置涨幅图表范围
        if len(self.price_changes_pct) > 0:
            change_min, change_max = self.price_changes_pct.min(), self.price_changes_pct.max()
            
            # 检查是否有nan值
            if np.isnan(change_min) or np.isnan(change_max):
                # 过滤掉nan值
                valid_changes = self.price_changes_pct[~np.isnan(self.price_changes_pct)]
                if len(valid_changes) > 0:
                    change_min, change_max = valid_changes.min(), valid_changes.max()
                else:
                    # 如果所有值都是nan，使用默认范围
                    change_min, change_max = -5, 5
            
            # 如果范围为0，设置一个小的默认范围
            if change_max == change_min:
                change_min -= 2.5
                change_max += 2.5
            
            change_range = change_max - change_min
            self.price_graph.setYRange(change_min - change_range * 0.1, change_max + change_range * 0.1)
        else:
            # 没有数据时设置默认范围
            self.price_graph.setYRange(-5, 5)
        
        # 设置成交量图表范围
        if len(self.volumes) > 0:
            volume_max = self.volumes.max()
            if np.isnan(volume_max) or volume_max == 0:
                volume_max = 1000  # 默认值
            self.volume_graph.setYRange(0, volume_max * 1.1)
        else:
            # 没有数据时设置默认范围
            self.volume_graph.setYRange(0, 1000)
        
        # 设置X轴范围为实际数据的时间范围
        if len(self.timestamps) > 0:
            time_min = self.timestamps.min()
            time_max = self.timestamps.max()
            if time_max > time_min:
                time_range = time_max - time_min
                # 添加一点边距
                margin = time_range * 0.02
                self.price_graph.setXRange(time_min - margin, time_max + margin)
                self.volume_graph.setXRange(time_min - margin, time_max + margin)
            else:
                # 如果只有一个数据点或时间范围为0，设置默认范围
                self.price_graph.setXRange(time_min - 3600, time_min + 3600)  # 前后各1小时
                self.volume_graph.setXRange(time_min - 3600, time_min + 3600)
        else:
            # 没有数据时设置默认时间范围
            import time
            current_time = time.time()
            self.price_graph.setXRange(current_time - 3600, current_time + 3600)
            self.volume_graph.setXRange(current_time - 3600, current_time + 3600)
        
        # 同步X轴
        self.volume_graph.setXLink(self.price_graph)
        
        # 在图表设置完成后，重新设置时间轴的时间映射
        if hasattr(self, 'original_times') and len(self.original_times) > 0:
            # 重新构建时间映射
            time_mapping = {}
            for i, (compressed_ts, original_time) in enumerate(zip(self.timestamps, self.original_times)):
                time_mapping[compressed_ts] = original_time
            
            # 设置时间轴的时间映射
            price_bottom_axis = self.price_graph.getAxis('bottom')
            volume_bottom_axis = self.volume_graph.getAxis('bottom')
            
            if hasattr(price_bottom_axis, 'setTimeMapping'):
                price_bottom_axis.setTimeMapping(time_mapping)
            if hasattr(volume_bottom_axis, 'setTimeMapping'):
                volume_bottom_axis.setTimeMapping(time_mapping)
        
        # 更新图例
        self.updateLegend()

    def setupInteractions(self):
        # 清理之前的事件代理
        if hasattr(self, 'proxy'):
            self.proxy.disconnect()
            del self.proxy
        if hasattr(self, 'proxy_volume'):
            self.proxy_volume.disconnect()
            del self.proxy_volume
        
        # 提示标签
        if not hasattr(self, 'label') or self.label is None:
            self.label = QLabel(self.price_graph)
            self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            self.label.setStyleSheet("""
                background-color: rgba(0, 0, 0, 200); 
                color: white;
                padding: 8px; 
                border: 1px solid gray;
                font-family: Consolas;
                font-size: 12px;
                min-width: 120px;
            """)
        self.label.hide()

        # 绑定事件
        self.proxy = pg.SignalProxy(
            self.price_graph.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.onMouseMove
        )
        
        # 为成交量图表也添加鼠标移动事件
        self.proxy_volume = pg.SignalProxy(
            self.volume_graph.scene().sigMouseMoved,
            rateLimit=60,
            slot=self.onMouseMoveVolume
        )

    def onMouseMove(self, evt):
        # 检查是否有线条数据
        if not self.price_lines or not self.line_data:
            if hasattr(self, 'label') and self.label is not None:
                self.label.hide()
            return
            
        pos = evt[0]
        if self.price_graph.sceneBoundingRect().contains(pos):
            mousePoint = self.price_graph.getPlotItem().vb.mapSceneToView(pos)
            x = mousePoint.x()
            y = mousePoint.y()

            # 查找最近的线条和数据点（只检测可见线条）
            closest_line_idx = -1
            closest_distance = float('inf')
            closest_data_idx = 0
            
            for line_idx, line_data in enumerate(self.line_data):
                # 跳过不可见的线条
                if line_idx >= len(self.line_visible) or not self.line_visible[line_idx]:
                    continue
                    
                timestamps = line_data['timestamps']
                price_changes = line_data['price_changes_pct']
                
                if len(timestamps) == 0:
                    continue
                
                # 查找最近的时间点
                data_idx = np.abs(timestamps - x).argmin()
                if 0 <= data_idx < len(timestamps):
                    # 计算鼠标到这个数据点的距离
                    point_x = timestamps[data_idx]
                    point_y = price_changes[data_idx]
                    
                    # 计算屏幕坐标系下的距离
                    distance = ((x - point_x) ** 2 + (y - point_y) ** 2) ** 0.5
                    
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_line_idx = line_idx
                        closest_data_idx = data_idx

            # 如果找到了最近的可见线条和数据点
            if closest_line_idx >= 0 and closest_line_idx < len(self.line_data) and closest_data_idx >= 0:
                line_data = self.line_data[closest_line_idx]
                line_name = self.line_names[closest_line_idx] if closest_line_idx < len(self.line_names) else f"线条 {closest_line_idx + 1}"
                line_color = self.line_colors[closest_line_idx] if closest_line_idx < len(self.line_colors) else "white"
                
                timestamps = line_data['timestamps']
                price_changes = line_data['price_changes_pct']
                volumes = line_data['volumes']
                original_times = line_data['original_times']
                
                if closest_data_idx < len(timestamps):
                    timestamp = timestamps[closest_data_idx]
                    change_pct = price_changes[closest_data_idx]
                    volume = volumes[closest_data_idx] if volumes is not None and closest_data_idx < len(volumes) else 0
                    
                    # 使用原始时间显示，如果有的话
                    if original_times is not None and closest_data_idx < len(original_times):
                        original_time = original_times[closest_data_idx]
                        if isinstance(original_time, pd.Timestamp):
                            date_str = original_time.strftime('%Y-%m-%d')
                            time_str = original_time.strftime('%H:%M')
                        else:
                            dt = pd.to_datetime(original_time)
                            date_str = dt.strftime('%Y-%m-%d')
                            time_str = dt.strftime('%H:%M')
                    else:
                        # 回退到使用压缩后的时间
                        dt = pd.to_datetime(timestamp, unit='s')
                        date_str = dt.strftime('%Y-%m-%d')
                        time_str = dt.strftime('%H:%M')

                    # 构建提示文本
                    line=line_name.split('\n')[0]
                    text = [
                        f"线条: {line}",
                        f"日期: {date_str}",
                        f"时间: {time_str}",
                        f"涨幅: {change_pct:+.2f}%",
                        f"成交量: {volume:.0f}"
                    ]

                    if hasattr(self, 'label') and self.label is not None:
                        self.label.setText("<br>".join(text))
                        self.label.setStyleSheet(f"""
                            background-color: rgba(0, 0, 0, 200); 
                            color: white;
                            padding: 8px; 
                            border: 2px solid {line_color};
                            font-family: Consolas;
                            font-size: 12px;
                            min-width: 120px;
                        """)
                        self.label.adjustSize()

                        # 更新标签位置，确保不超出边界
                        label_pos = self.price_graph.mapFromScene(pos)
                        label_x = min(max(label_pos.x() + 15, 0), self.price_graph.width() - self.label.width())
                        label_y = min(max(label_pos.y() + 15, 0), self.price_graph.height() - self.label.height())
                        self.label.move(label_x, label_y)
                        self.label.show()
            else:
                # 没有找到可见线条，隐藏标签
                if hasattr(self, 'label') and self.label is not None:
                    self.label.hide()
        else:
            if hasattr(self, 'label') and self.label is not None:
                self.label.hide()
    
    def onMouseMoveVolume(self, evt):
        # 成交量图表的鼠标移动事件（可以复用价格图的逻辑）
        self.onMouseMove(evt)

    def leaveEvent(self, event):
        """当鼠标离开MultiLineChart组件时隐藏标签"""
        if hasattr(self, 'label') and self.label is not None:
            self.label.hide()
        super().leaveEvent(event)

    def getRandomColor(self):
        """生成随机颜色，避免与背景色和已使用颜色重叠"""
        import random
        
        # 预定义的颜色列表，避免黑色和已使用的颜色
        available_colors = [
            '#FF6B6B',  # 红色
            '#4ECDC4',  # 青色
            '#45B7D1',  # 蓝色
            '#96CEB4',  # 绿色
            '#FFEAA7',  # 黄色
            '#DDA0DD',  # 紫色
            '#98D8C8',  # 薄荷绿
            '#F7DC6F',  # 金色
            '#BB8FCE',  # 淡紫色
            '#85C1E9',  # 天蓝色
            '#F8C471',  # 橙色
            '#82E0AA',  # 浅绿色
            '#F1948A',  # 粉红色
            '#85C1E9',  # 浅蓝色
            '#D7BDE2',  # 薰衣草色
            '#A9DFBF',  # 浅绿色
        ]
        
        # 过滤掉已使用的颜色
        unused_colors = [color for color in available_colors if color not in self.used_colors]
        
        if not unused_colors:
            # 如果所有预定义颜色都用完了，生成随机颜色
            while True:
                r = random.randint(50, 255)  # 避免太暗的颜色
                g = random.randint(50, 255)
                b = random.randint(50, 255)
                color = f'#{r:02x}{g:02x}{b:02x}'
                if color not in self.used_colors:
                    break
        else:
            color = random.choice(unused_colors)
        
        self.used_colors.add(color)
        return color

    def updateLegend(self):
        """更新图例显示"""
        # 清除之前的图例项
        for i in reversed(range(self.legend_layout.count())):
            item = self.legend_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                    self.legend_layout.removeItem(item)
        
        # 添加新的图例项
        for i, (name, color, visible) in enumerate(zip(self.line_names, self.line_colors, self.line_visible)):
            # 创建图例项容器
            legend_item = QWidget()
            legend_item.setStyleSheet("background-color: transparent;")
            
            # 创建水平布局
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(5, 2, 5, 2)
            item_layout.setSpacing(8)
            
            # 复选框（缩小到80%，选中时绿色背景）
            checkbox = QCheckBox()
            checkbox.setChecked(visible)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-size: 12px;
                    background: transparent;
                }
                QCheckBox::indicator {
                    width: 13px;  /* 原16px，80% */
                    height: 13px;
                    border: 2px solid #555;
                    border-radius: 3px;
                    background-color: transparent;
                }
                QCheckBox::indicator:checked {
                    background-color: #4CAF50;  /* 绿色背景 */
                    border: 2px solid #4CAF50;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                }
                QCheckBox::indicator:unchecked {
                    background-color: transparent;
                    border: 2px solid #555;
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #777;
                }
            """)
            checkbox.stateChanged.connect(lambda state, idx=i: self.toggleLineVisibility(idx, state == 2))
            
            # 圆形颜色块（放大到140%）
            # color_indicator = QLabel("●")
            # color_indicator.setStyleSheet(
            #     f"color: {color}; font-size: 22px; font-weight: bold;"
            # )
            # color_indicator.setFixedWidth(28)
            # color_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 线条名称
            name_label = QLabel(name)
            name_label.setStyleSheet(
                f"color: {color}; font-size: 12px; font-weight: bold;"
            )
  
            name_label.setWordWrap(True)
            
            item_layout.addWidget(checkbox)
            # item_layout.addWidget(color_indicator)
            item_layout.addWidget(name_label)
            item_layout.addStretch()
            
            legend_item.setLayout(item_layout)
            
            self.legend_layout.addWidget(legend_item)
        
        self.legend_layout.addStretch()  # 只在最后加一次
    
    def toggleLineVisibility(self, line_index, visible):
        """切换线条的可见性
        
        Args:
            line_index: 线条索引
            visible: 是否可见
        """
        if 0 <= line_index < len(self.price_lines):
            # 更新可见性状态
            self.line_visible[line_index] = visible
            
            # 获取线条对象
            line = self.price_lines[line_index]
            
            if visible:
                # 显示线条
                if line not in self.price_graph.listDataItems():
                    self.price_graph.addItem(line)
                print(f"显示线条: {self.line_names[line_index]}")
            else:
                # 隐藏线条
                if line in self.price_graph.listDataItems():
                    self.price_graph.removeItem(line)
                print(f"隐藏线条: {self.line_names[line_index]}")

    def clearAllLines(self):
        """清除所有线条"""
        self.clearCharts()
        self.updateLegend()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data_file = r'D:\ave_price.csv'
    main_window = QWidget()
    main_window.setWindowTitle("股票图表 - 实时数据显示")
    main_window.resize(1200, 700)
    main_window.setStyleSheet("background-color: black;")

    # 传递数据文件参数给图表组件
    chart = MultiLineChart(data_file=data_file,clear_all=False)
    layout = QVBoxLayout()
    layout.addWidget(chart)
    main_window.setLayout(layout)

    main_window.show()
    sys.exit(app.exec())  

这是一个股票分时图的代码，在X轴中能显示多天的数据。现在我需要实现如下功能，在【清除所有】按钮下面增加两个按钮，分别是+天数，-天数。当点击增加天数时，在X轴上就过滤掉左侧最远的一天数据，当点击增加天数时，将最近过滤的日期数据显示出来。本质上是要对X轴上的日间进行缩放，缩放的步长为1天。
    '''
    output = start_conversation_gemini(test)
    print('===>  ' + output)
    # for model_idx in range(5):
    #     output = start_conversation_gemini('what is your name ?', model_idx)
    #     print(models_data[model_idx]['model_id'] + '===>  ' + output)
