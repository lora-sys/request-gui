import pandas as pd
import time
import os
import logging
try:
    from DrissionPage import ChromiumPage
    from DataRecorder import Recorder
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False

class MaoyanSpider:
    def __init__(self):
        self.movies_data = []
        # 兼容Python 3.8的日志配置
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('data.log', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(fh)

    def crawl(self, callback=None):
        if not DRISSION_AVAILABLE:
            raise ImportError("请先安装 DrissionPage: pip install DrissionPage")
        page = ChromiumPage()
        all_data = []
        page.get('https://www.maoyan.com/board/4')
        page_num = 1
        while True:
            if callback:
                callback((page_num-1)*10)
            for mov in list(page.eles('t:dd')):
                try:
                    num = mov('t:i').text
                    score = mov('.score').text
                    title = mov('@data-act=boarditem-click').attr('title')
                    star = mov('.star').text.strip()[3:] if mov('.star') else ''
                    time_str = mov('.releasetime').text.strip()[5:] if mov('.releasetime') else ''
                    # 提取年份
                    import re
                    year_match = re.search(r'(\d{4})', time_str)
                    year = int(year_match.group(1)) if year_match else None
                    all_data.append({
                        'rank': int(num),
                        'name': title,
                        'star': star,
                        'score': float(score),
                        'release_time': time_str,
                        'year': year
                    })
                    logging.debug(f'记录电影信息: {num}, {title}, {star}, {time_str}, {score}')
                except Exception as e:
                    logging.error(f'解析电影数据失败: {e}')
                    continue
            # 下一页
            btn = page('下一页', timeout=2)
            if btn:
                btn.click()
                page.wait.load_start()
                page_num += 1
                time.sleep(2)
            else:
                break
        if callback:
            callback(len(all_data))
        self.movies_data = all_data
        return pd.DataFrame(self.movies_data)

    def save_to_csv(self, df, filename='maoyan_top100.csv'):
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"数据已成功保存到: {filename}")
        except Exception as e:
            print(f"保存数据失败: {e}")
            raise

def main():
    spider = MaoyanSpider()
    try:
        df = spider.crawl(callback=lambda x: print(f"爬取进度: {x}%"))
        spider.save_to_csv(df)
        print("爬取完成！数据已保存到maoyan_top100.csv")
    except Exception as e:
        print(f"爬取过程出现错误: {e}")

if __name__ == "__main__":
    main() 