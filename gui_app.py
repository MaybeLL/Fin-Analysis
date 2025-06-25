#!/usr/bin/env python3
"""
股票新闻分析工具 - GUI版本
基于Tkinter的现代化界面应用
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Any
from stock_news_analyzer import StockNewsAnalyzer, NewsDatabase
import os


class StockNewsGUI:
    """股票新闻分析GUI应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📈 股票新闻情感分析仪表板")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 设置应用图标和样式
        self.setup_styles()
        
        # 初始化数据
        self.analyzer = StockNewsAnalyzer()
        self.database = NewsDatabase()
        self.monitored_stocks = self.analyzer.config.get("stocks", [])
        self.selected_stock = tk.StringVar(value=self.monitored_stocks[0] if self.monitored_stocks else "")
        self.time_range = tk.IntVar(value=7)
        
        # 定时任务控制
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # 创建主界面
        self.create_main_interface()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 初始化加载数据
        self.refresh_overview()
    
    def setup_styles(self):
        """设置UI样式"""
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 自定义样式
        style.configure('Title.TLabel', 
                       font=('SF Pro Display', 16, 'bold'),
                       background='#f0f0f0',
                       foreground='#1d1d1f')
        
        style.configure('Heading.TLabel',
                       font=('SF Pro Display', 12, 'bold'),
                       background='#f0f0f0',
                       foreground='#1d1d1f')
        
        style.configure('Info.TLabel',
                       font=('SF Pro Text', 10),
                       background='#f0f0f0',
                       foreground='#424245')
        
        style.configure('Card.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Success.TButton',
                       font=('SF Pro Text', 10, 'bold'),
                       foreground='white')
        
        style.map('Success.TButton',
                 background=[('active', '#34c759'), ('!active', '#30d158')])
    
    def create_main_interface(self):
        """创建主界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="📈 股票新闻情感分析仪表板", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # 创建各个界面区域
        self.create_stock_management_section(main_frame, row=1)
        self.create_control_section(main_frame, row=2)
        self.create_overview_section(main_frame, row=3)
        self.create_detail_section(main_frame, row=4)
        self.create_status_section(main_frame, row=5)
    
    def create_stock_management_section(self, parent, row):
        """创建股票管理区域"""
        # 股票管理框架
        stock_frame = ttk.LabelFrame(parent, text="🎯 股票管理", padding="15")
        stock_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        stock_frame.columnconfigure(1, weight=1)
        
        # 当前监控列表
        ttk.Label(stock_frame, text="当前监控:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # 股票标签容器
        self.stock_tags_frame = ttk.Frame(stock_frame)
        self.stock_tags_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        # 添加股票区域
        add_frame = ttk.Frame(stock_frame)
        add_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        ttk.Label(add_frame, text="添加股票:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.stock_entry = ttk.Entry(add_frame, width=15, font=('SF Pro Text', 11))
        self.stock_entry.grid(row=0, column=1, padx=(0, 10))
        self.stock_entry.bind('<Return>', lambda e: self.add_stock())
        
        add_button = ttk.Button(add_frame, text="添加", command=self.add_stock, style='Success.TButton')
        add_button.grid(row=0, column=2, padx=(0, 20))
        
        ttk.Label(add_frame, text="💡 示例: NVDA, META, NFLX", style='Info.TLabel').grid(row=0, column=3, sticky=tk.W)
        
        # 更新股票标签显示
        self.update_stock_tags()
    
    def create_control_section(self, parent, row):
        """创建控制区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(2, weight=1)
        
        # 股票选择
        ttk.Label(control_frame, text="🔍 分析选择:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        stock_combo = ttk.Combobox(control_frame, textvariable=self.selected_stock, 
                                  values=self.monitored_stocks, state='readonly', width=15)
        stock_combo.grid(row=0, column=1, padx=(0, 30))
        stock_combo.bind('<<ComboboxSelected>>', lambda e: self.on_stock_selected())
        
        # 时间范围
        ttk.Label(control_frame, text="📅 时间范围:", style='Heading.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        time_frame = ttk.Frame(control_frame)
        time_frame.grid(row=0, column=3, padx=(0, 30))
        
        time_options = [(1, "1天"), (3, "3天"), (7, "7天"), (14, "14天"), (30, "30天")]
        for i, (value, text) in enumerate(time_options):
            rb = ttk.Radiobutton(time_frame, text=text, variable=self.time_range, 
                               value=value, command=self.on_time_range_changed)
            rb.grid(row=0, column=i, padx=(0, 10))
        
        # 操作按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=(15, 0), sticky=tk.W)
        
        ttk.Button(button_frame, text="🔄 刷新数据", command=self.refresh_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="📊 生成报告", command=self.generate_report).grid(row=0, column=1, padx=(0, 10))
        
        self.scheduler_button = ttk.Button(button_frame, text="▶️ 启动定时任务", command=self.toggle_scheduler)
        self.scheduler_button.grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(button_frame, text="⚙️ 设置", command=self.open_settings).grid(row=0, column=3, padx=(0, 10))
    
    def create_overview_section(self, parent, row):
        """创建概览区域"""
        overview_frame = ttk.LabelFrame(parent, text="📊 实时概览", padding="15")
        overview_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        overview_frame.columnconfigure(0, weight=1)
        
        # 创建滚动区域
        canvas = tk.Canvas(overview_frame, height=150, bg='white')
        scrollbar = ttk.Scrollbar(overview_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(xscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.overview_canvas = canvas
        self.overview_frame = scrollable_frame
    
    def create_detail_section(self, parent, row):
        """创建详细分析区域"""
        detail_frame = ttk.LabelFrame(parent, text="📈 详细分析", padding="15")
        detail_frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        # 创建文本区域
        text_frame = ttk.Frame(detail_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.detail_text = tk.Text(text_frame, height=15, wrap=tk.WORD, 
                                  font=('SF Pro Text', 11), bg='white', fg='#1d1d1f')
        scrollbar_v = ttk.Scrollbar(text_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=scrollbar_v.set)
        
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def create_status_section(self, parent, row):
        """创建状态区域"""
        status_frame = ttk.LabelFrame(parent, text="🔧 系统状态", padding="15")
        status_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # 状态信息
        self.status_labels = {}
        
        status_info = [
            ("💡 分析引擎:", "轻量级金融分析器"),
            ("🔄 最后更新:", "未更新"),
            ("📦 数据库:", "stock_news.db"),
            ("⏰ 下次更新:", "未设置"),
            ("📋 监控列表:", "")
        ]
        
        for i, (label, value) in enumerate(status_info):
            ttk.Label(status_frame, text=label, style='Info.TLabel').grid(row=i, column=0, sticky=tk.W, padx=(0, 10))
            self.status_labels[label] = ttk.Label(status_frame, text=value, style='Info.TLabel')
            self.status_labels[label].grid(row=i, column=1, sticky=tk.W)
        
        self.update_status_info()
    
    def update_stock_tags(self):
        """更新股票标签显示"""
        # 清除现有标签
        for widget in self.stock_tags_frame.winfo_children():
            widget.destroy()
        
        # 创建新标签
        for i, stock in enumerate(self.monitored_stocks):
            tag_frame = ttk.Frame(self.stock_tags_frame)
            tag_frame.grid(row=0, column=i, padx=(0, 5))
            
            stock_label = ttk.Label(tag_frame, text=stock, 
                                   font=('SF Pro Text', 10, 'bold'),
                                   foreground='white', background='#007AFF',
                                   padding="5 3")
            stock_label.grid(row=0, column=0)
            
            remove_button = ttk.Button(tag_frame, text="×", width=3,
                                     command=lambda s=stock: self.remove_stock(s))
            remove_button.grid(row=0, column=1, padx=(2, 0))
        
        # 更新组合框选项
        if hasattr(self, 'selected_stock'):
            stock_combo_values = self.monitored_stocks
            # 更新组合框的值
            for widget in self.root.winfo_children():
                self._update_combobox_recursive(widget, stock_combo_values)
    
    def _update_combobox_recursive(self, widget, values):
        """递归更新组合框选项"""
        if isinstance(widget, ttk.Combobox) and widget['textvariable'] == str(self.selected_stock):
            widget['values'] = values
            if values and not self.selected_stock.get():
                self.selected_stock.set(values[0])
        
        for child in widget.winfo_children():
            self._update_combobox_recursive(child, values)
    
    def add_stock(self):
        """添加股票"""
        stock_code = self.stock_entry.get().strip().upper()
        
        if not stock_code:
            return
        
        if stock_code in self.monitored_stocks:
            messagebox.showwarning("重复股票", f"{stock_code} 已在监控列表中")
            return
        
        # 验证股票代码格式
        if not self._validate_stock_code(stock_code):
            messagebox.showerror("无效代码", f"{stock_code} 不是有效的股票代码")
            return
        
        # 添加到列表
        self.monitored_stocks.append(stock_code)
        self.update_stock_tags()
        
        # 更新配置文件
        self.analyzer.config["stocks"] = self.monitored_stocks
        self._save_config()
        
        # 设置选中新添加的股票
        self.selected_stock.set(stock_code)
        
        # 清空输入框
        self.stock_entry.delete(0, tk.END)
        
        # 获取新股票数据
        self.refresh_data_for_stock(stock_code)
        
        messagebox.showinfo("添加成功", f"已添加 {stock_code} 到监控列表")
    
    def remove_stock(self, stock_code):
        """移除股票"""
        if messagebox.askyesno("确认删除", f"确定要移除 {stock_code} 吗？"):
            self.monitored_stocks.remove(stock_code)
            self.update_stock_tags()
            
            # 更新配置文件
            self.analyzer.config["stocks"] = self.monitored_stocks
            self._save_config()
            
            # 如果删除的是当前选中的股票，切换到第一个
            if self.selected_stock.get() == stock_code:
                if self.monitored_stocks:
                    self.selected_stock.set(self.monitored_stocks[0])
                else:
                    self.selected_stock.set("")
            
            self.refresh_overview()
            self.update_detail_view()
    
    def _validate_stock_code(self, code):
        """验证股票代码"""
        # 简单验证：1-5个字母
        import re
        return bool(re.match(r'^[A-Z]{1,5}$', code))
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.analyzer.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def refresh_data(self):
        """刷新所有数据"""
        def refresh_thread():
            try:
                self.analyzer.run_once()
                self.root.after(0, self.on_refresh_complete)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("刷新失败", str(e)))
        
        # 在后台线程中运行
        threading.Thread(target=refresh_thread, daemon=True).start()
        messagebox.showinfo("刷新中", "正在后台刷新数据，请稍候...")
    
    def refresh_data_for_stock(self, stock_code):
        """为单个股票刷新数据"""
        def refresh_stock_thread():
            try:
                self.analyzer.collect_news_for_stock(stock_code)
                self.root.after(0, self.on_refresh_complete)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("刷新失败", str(e)))
        
        threading.Thread(target=refresh_stock_thread, daemon=True).start()
    
    def on_refresh_complete(self):
        """刷新完成回调"""
        self.refresh_overview()
        self.update_detail_view()
        self.update_status_info()
        messagebox.showinfo("刷新完成", "数据已更新")
    
    def refresh_overview(self):
        """刷新概览区域"""
        # 清除现有内容
        for widget in self.overview_frame.winfo_children():
            widget.destroy()
        
        # 为每个股票创建卡片
        for i, stock in enumerate(self.monitored_stocks):
            self.create_stock_card(self.overview_frame, stock, i)
        
        # 更新滚动区域
        self.overview_frame.update_idletasks()
        self.overview_canvas.configure(scrollregion=self.overview_canvas.bbox("all"))
    
    def create_stock_card(self, parent, stock, column):
        """创建股票卡片"""
        # 获取股票数据
        report = self.analyzer.generate_analysis_report(stock, self.time_range.get())
        
        # 创建卡片框架
        card = ttk.Frame(parent, style='Card.TFrame', padding="10")
        card.grid(row=0, column=column, padx=(0, 10), sticky=(tk.N, tk.S))
        
        # 股票名称
        name_label = ttk.Label(card, text=stock, font=('SF Pro Display', 12, 'bold'))
        name_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        if 'error' in report:
            # 显示错误信息
            error_label = ttk.Label(card, text="无数据", foreground='gray')
            error_label.grid(row=1, column=0, columnspan=2)
        else:
            # 情感分布
            sentiment = report['sentiment_distribution']
            total = report['total_news']
            
            sentiments = [
                ('😊', sentiment['positive'], '#34C759'),
                ('😐', sentiment['neutral'], '#8E8E93'),
                ('😞', sentiment['negative'], '#FF3B30')
            ]
            
            for i, (emoji, count, color) in enumerate(sentiments):
                if total > 0:
                    percentage = int(count * 100 / total)
                    text = f"{emoji} {percentage}%"
                else:
                    text = f"{emoji} 0%"
                
                label = ttk.Label(card, text=text, font=('SF Pro Text', 10))
                label.grid(row=i+1, column=0, sticky=tk.W, pady=1)
            
            # 新闻总数
            count_label = ttk.Label(card, text=f"{total}条", font=('SF Pro Text', 10, 'bold'))
            count_label.grid(row=4, column=0, pady=(5, 0))
            
            # 详情按钮
            detail_button = ttk.Button(card, text="详情", width=8,
                                     command=lambda s=stock: self.show_stock_detail(s))
            detail_button.grid(row=5, column=0, pady=(5, 0))
    
    def show_stock_detail(self, stock):
        """显示股票详情"""
        self.selected_stock.set(stock)
        self.update_detail_view()
    
    def update_detail_view(self):
        """更新详细分析视图"""
        stock = self.selected_stock.get()
        if not stock:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, "请选择要分析的股票")
            return
        
        # 生成报告
        report = self.analyzer.generate_analysis_report(stock, self.time_range.get())
        
        # 格式化显示
        content = self._format_report(stock, report)
        
        # 更新文本区域
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, content)
    
    def _format_report(self, stock, report):
        """格式化报告内容"""
        if 'error' in report:
            return f"❌ {stock} - {report['error']}"
        
        content = f"📈 {stock} 详细分析报告\n"
        content += "=" * 50 + "\n\n"
        
        content += f"📊 总览信息:\n"
        content += f"• 📰 新闻总数: {report['total_news']}条\n"
        content += f"• 📊 平均情感: {report['average_sentiment_score']:.3f}\n"
        content += f"• 🎯 整体情感: {report['overall_sentiment']}\n"
        content += f"• 📅 分析时间: 最近{report['period_days']}天\n\n"
        
        content += f"📈 情感分布:\n"
        sentiment = report['sentiment_distribution']
        total = report['total_news']
        
        if total > 0:
            pos_pct = int(sentiment['positive'] * 100 / total)
            neu_pct = int(sentiment['neutral'] * 100 / total)
            neg_pct = int(sentiment['negative'] * 100 / total)
            
            content += f"• 🟢 正面: {sentiment['positive']}条 ({pos_pct}%)\n"
            content += f"• ⚪ 中性: {sentiment['neutral']}条 ({neu_pct}%)\n"
            content += f"• 🔴 负面: {sentiment['negative']}条 ({neg_pct}%)\n\n"
        
        content += f"📰 最新头条 (最近5条):\n"
        for i, headline in enumerate(report['recent_headlines'][:5], 1):
            content += f"{i}. {headline}\n"
        
        content += f"\n⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return content
    
    def generate_report(self):
        """生成并保存报告"""
        if not self.selected_stock.get():
            messagebox.showwarning("未选择股票", "请先选择要生成报告的股票")
            return
        
        try:
            stock = self.selected_stock.get()
            report = self.analyzer.generate_analysis_report(stock, self.time_range.get())
            
            # 格式化报告
            content = self._format_report(stock, report)
            
            # 保存文件
            filename = f"{stock}_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("报告已保存", f"报告已保存到:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("生成失败", f"生成报告失败: {str(e)}")
    
    def toggle_scheduler(self):
        """切换定时任务状态"""
        if self.scheduler_running:
            self.stop_scheduler()
        else:
            self.start_scheduler()
    
    def start_scheduler(self):
        """启动定时任务"""
        self.scheduler_running = True
        self.scheduler_button.configure(text="⏸️ 停止定时任务")
        
        def scheduler_worker():
            interval = self.analyzer.config.get("schedule", {}).get("interval_hours", 4) * 3600
            while self.scheduler_running:
                time.sleep(60)  # 每分钟检查一次
                if int(time.time()) % interval == 0:
                    try:
                        self.analyzer.run_once()
                        self.root.after(0, self.on_refresh_complete)
                    except Exception as e:
                        print(f"定时任务执行失败: {e}")
        
        self.scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        
        self.update_status_info()
        messagebox.showinfo("定时任务", "定时任务已启动")
    
    def stop_scheduler(self):
        """停止定时任务"""
        self.scheduler_running = False
        self.scheduler_button.configure(text="▶️ 启动定时任务")
        self.update_status_info()
        messagebox.showinfo("定时任务", "定时任务已停止")
    
    def open_settings(self):
        """打开设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ 设置")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#f0f0f0')
        
        # 设置内容
        ttk.Label(settings_window, text="⚙️ 系统设置", style='Title.TLabel').pack(pady=20)
        
        # API设置
        api_frame = ttk.LabelFrame(settings_window, text="API配置", padding="15")
        api_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(api_frame, text="Alpha Vantage API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        alpha_entry = ttk.Entry(api_frame, width=40)
        alpha_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        alpha_entry.insert(0, self.analyzer.config.get("api_keys", {}).get("alpha_vantage", ""))
        
        ttk.Label(api_frame, text="Finnhub API Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        finnhub_entry = ttk.Entry(api_frame, width=40)
        finnhub_entry.grid(row=1, column=1, padx=(10, 0), pady=5)
        finnhub_entry.insert(0, self.analyzer.config.get("api_keys", {}).get("finnhub", ""))
        
        # 定时设置
        schedule_frame = ttk.LabelFrame(settings_window, text="定时任务", padding="15")
        schedule_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(schedule_frame, text="更新间隔(小时):").grid(row=0, column=0, sticky=tk.W, pady=5)
        interval_var = tk.StringVar(value=str(self.analyzer.config.get("schedule", {}).get("interval_hours", 4)))
        interval_entry = ttk.Entry(schedule_frame, textvariable=interval_var, width=10)
        interval_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        # 保存按钮
        def save_settings():
            try:
                self.analyzer.config["api_keys"]["alpha_vantage"] = alpha_entry.get()
                self.analyzer.config["api_keys"]["finnhub"] = finnhub_entry.get()
                self.analyzer.config["schedule"]["interval_hours"] = int(interval_var.get())
                
                self._save_config()
                messagebox.showinfo("设置", "设置已保存")
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror("保存失败", str(e))
        
        ttk.Button(settings_window, text="保存设置", command=save_settings).pack(pady=20)
    
    def update_status_info(self):
        """更新状态信息"""
        # 分析引擎状态
        engine_status = "FinBERT (已安装)" if self.analyzer.collector else "轻量级金融分析器"
        self.status_labels["💡 分析引擎:"].configure(text=engine_status)
        
        # 最后更新时间
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status_labels["🔄 最后更新:"].configure(text=last_update)
        
        # 数据库信息
        try:
            db_size = os.path.getsize('stock_news.db') if os.path.exists('stock_news.db') else 0
            db_info = f"stock_news.db ({db_size // 1024}KB)"
        except:
            db_info = "stock_news.db"
        self.status_labels["📦 数据库:"].configure(text=db_info)
        
        # 下次更新时间
        if self.scheduler_running:
            interval = self.analyzer.config.get("schedule", {}).get("interval_hours", 4)
            next_update = f"{interval}小时后"
        else:
            next_update = "未设置"
        self.status_labels["⏰ 下次更新:"].configure(text=next_update)
        
        # 监控列表
        stocks_text = ", ".join(self.monitored_stocks) if self.monitored_stocks else "无"
        self.status_labels["📋 监控列表:"].configure(text=stocks_text)
    
    def on_stock_selected(self):
        """股票选择改变事件"""
        self.update_detail_view()
    
    def on_time_range_changed(self):
        """时间范围改变事件"""
        self.refresh_overview()
        self.update_detail_view()
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.scheduler_running:
            if messagebox.askyesno("确认退出", "定时任务正在运行，确定要退出吗？"):
                self.scheduler_running = False
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    app = StockNewsGUI()
    app.run()