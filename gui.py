import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from spider import MaoyanSpider
import threading
import os

class MaoyanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("猫眼电影Top100爬虫")
        self.root.geometry("400x200")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建爬取按钮
        self.crawl_btn = ttk.Button(self.main_frame, text="开始爬取榜单", command=self.start_crawl)
        self.crawl_btn.pack(pady=20)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_bar.pack(pady=10)
        
        self.spider = MaoyanSpider()
        self.crawling = False

    def update_progress(self, value):
        """更新进度条和状态"""
        self.progress_var.set(value)
        self.status_var.set(f"正在爬取第{value//10}页...")
        self.root.update()

    def generate_visualizations(self, df):
        """生成并保存所有可视化图表"""
        # 创建可视化目录
        if not os.path.exists('visualizations'):
            os.makedirs('visualizations')
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        try:
            # 1. 评分分布直方图
            plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x='score', bins=15)
            plt.title("Top100电影评分分布")
            plt.xlabel("评分")
            plt.ylabel("电影数量")
            plt.savefig('visualizations/评分分布.png')
            plt.close()
            
            # 2. 上映年份分布
            plt.figure(figsize=(12, 6))
            df['year'].value_counts().sort_index().plot(kind='bar')
            plt.title("电影上映年份分布")
            plt.xlabel("年份")
            plt.ylabel("电影数量")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('visualizations/年份分布.png')
            plt.close()
            
            # 3. 评分TOP10电影
            plt.figure(figsize=(12, 6))
            top10 = df.nlargest(10, 'score')
            sns.barplot(data=top10, y='name', x='score')
            plt.title("评分TOP10电影")
            plt.xlabel("评分")
            plt.ylabel("电影名称")
            plt.tight_layout()
            plt.savefig('visualizations/TOP10电影.png')
            plt.close()
            
            # 4. 评分与年份关系
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=df, x='year', y='score')
            sns.regplot(data=df, x='year', y='score', scatter=False)
            plt.title("评分与年份关系")
            plt.xlabel("年份")
            plt.ylabel("评分")
            plt.savefig('visualizations/评分年份关系.png')
            plt.close()
            
            return True
        except Exception as e:
            print(f"生成图表时出错: {e}")
            return False

    def start_crawl(self):
        """开始爬取数据"""
        if not self.crawling:
            self.crawling = True
            self.crawl_btn.configure(state=tk.DISABLED)
            
            # 在新线程中运行爬虫
            thread = threading.Thread(target=self.crawl_data)
            thread.daemon = True
            thread.start()

    def crawl_data(self):
        """爬取数据并生成图表"""
        try:
            # 爬取数据
            df = self.spider.crawl(callback=self.update_progress)
            
            # 保存CSV文件
            self.spider.save_to_csv(df)
            
            # 生成并保存图表
            self.status_var.set("正在生成可视化图表...")
            if self.generate_visualizations(df):
                self.status_var.set("完成！数据和图表已保存")
                messagebox.showinfo("成功", "数据爬取完成！\n图表已保存到visualizations目录")
            else:
                self.status_var.set("图表生成失败，请查看控制台输出")
                
        except Exception as e:
            self.status_var.set(f"爬取失败：{str(e)}")
            messagebox.showerror("错误", f"爬取过程中出现错误：{str(e)}")
        finally:
            self.crawling = False
            self.crawl_btn.configure(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = MaoyanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 