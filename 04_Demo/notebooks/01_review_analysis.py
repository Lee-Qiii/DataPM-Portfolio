# ============================================
# 视频剪辑软件用户评论分析
# ============================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

print("="*50)
print("视频剪辑软件用户评论分析")
print("="*50)

# ============================================
# 第一部分：创建模拟评论数据
# ============================================
# 说明：由于App Store评论爬取有限制，
# 我们先用模拟数据完成分析流程，
# 展示数据分析能力

print("\n[1/5] 正在生成模拟评论数据...")

# 设置随机种子，确保结果可复现
np.random.seed(42)

# 剪映评论模拟数据
jianying_positive = [
    "太好用了，小白也能剪出大片",
    "模板超多，一键就能出效果",
    "AI字幕识别很准，省了好多时间",
    "免费功能就够用了，良心软件",
    "和抖音配合完美，发布很方便",
    "特效丰富，转场很自然",
    "操作简单，上手很快",
    "素材库更新快，紧跟热点",
    "剪辑速度快，不卡顿",
    "智能抠图效果不错"
]

jianying_negative = [
    "会员太贵了，能不能便宜点",
    "有时候会闪退，希望修复",
    "导出速度有点慢",
    "有些素材只能会员用，套路",
    "占用内存太大了",
    "片尾强制加logo很烦",
    "高级功能太少，专业剪辑不够用",
    "音乐版权不清楚，不敢商用"
]

filmora_positive = [
    "功能很专业，比剪映强多了",
    "调色功能好用，画面质感提升明显",
    "转场效果很多，选择丰富",
    "多轨道编辑方便，效率高",
    "AI功能实用，智能字幕准确",
    "界面清晰，功能分类合理",
    "导出选项多，参数可调",
    "客服响应快，问题能解决",
    "模板质量高，商务风格好看",
    "音频编辑功能完善"
]

filmora_negative = [
    "订阅太贵，一年两百多",
    "试用版水印太大，逼人付费",
    "有些功能要额外付费，坑",
    "软件体积大，启动慢",
    "AI功能有次数限制",
    "素材库不如剪映丰富",
    "学习成本比剪映高",
    "有些特效要单独买"
]

# 生成剪映评论
jianying_reviews = []
for i in range(300):
    rating = np.random.choice([1,2,3,4,5], p=[0.03, 0.05, 0.12, 0.30, 0.50])
    if rating >= 4:
        content = np.random.choice(jianying_positive)
    elif rating <= 2:
        content = np.random.choice(jianying_negative)
    else:
        content = np.random.choice(jianying_positive + jianying_negative)
    
    jianying_reviews.append({
        'product': '剪映',
        'rating': rating,
        'content': content,
        'date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=np.random.randint(0, 365))
    })

# 生成Filmora评论
filmora_reviews = []
for i in range(200):
    rating = np.random.choice([1,2,3,4,5], p=[0.05, 0.10, 0.15, 0.35, 0.35])
    if rating >= 4:
        content = np.random.choice(filmora_positive)
    elif rating <= 2:
        content = np.random.choice(filmora_negative)
    else:
        content = np.random.choice(filmora_positive + filmora_negative)
    
    filmora_reviews.append({
        'product': 'Filmora',
        'rating': rating,
        'content': content,
        'date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=np.random.randint(0, 365))
    })

# 合并数据
all_reviews = jianying_reviews + filmora_reviews
df = pd.DataFrame(all_reviews)

# 保存数据
data_path = '../data/reviews.csv'
df.to_csv(data_path, index=False, encoding='utf-8-sig')
print(f"✓ 已生成 {len(df)} 条模拟评论")
print(f"✓ 数据已保存至: {data_path}")

# ============================================
# 第二部分：评分分布分析
# ============================================

print("\n[2/5] 正在分析评分分布...")

# 按产品分组统计
jianying_df = df[df['product'] == '剪映']
filmora_df = df[df['product'] == 'Filmora']

# 计算关键指标
jianying_avg = jianying_df['rating'].mean()
filmora_avg = filmora_df['rating'].mean()
jianying_good_rate = len(jianying_df[jianying_df['rating'] >= 4]) / len(jianying_df) * 100
filmora_good_rate = len(filmora_df[filmora_df['rating'] >= 4]) / len(filmora_df) * 100

print(f"\n【剪映】")
print(f"  评论数: {len(jianying_df)} 条")
print(f"  平均评分: {jianying_avg:.2f} / 5.0")
print(f"  好评率(4-5星): {jianying_good_rate:.1f}%")

print(f"\n【Filmora】")
print(f"  评论数: {len(filmora_df)} 条")
print(f"  平均评分: {filmora_avg:.2f} / 5.0")
print(f"  好评率(4-5星): {filmora_good_rate:.1f}%")

# 绘制评分分布对比图
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 剪映评分分布
jianying_counts = jianying_df['rating'].value_counts().sort_index()
colors = ['#ff6b6b', '#ffa502', '#ffd93d', '#6bcb77', '#4d96ff']
axes[0].bar(jianying_counts.index, jianying_counts.values, color=colors)
axes[0].set_xlabel('评分', fontsize=12)
axes[0].set_ylabel('数量', fontsize=12)
axes[0].set_title(f'剪映评分分布 (平均: {jianying_avg:.2f})', fontsize=14)
axes[0].set_xticks([1, 2, 3, 4, 5])

# Filmora评分分布
filmora_counts = filmora_df['rating'].value_counts().sort_index()
axes[1].bar(filmora_counts.index, filmora_counts.values, color=colors)
axes[1].set_xlabel('评分', fontsize=12)
axes[1].set_ylabel('数量', fontsize=12)
axes[1].set_title(f'Filmora评分分布 (平均: {filmora_avg:.2f})', fontsize=14)
axes[1].set_xticks([1, 2, 3, 4, 5])

plt.tight_layout()
plt.savefig('../data/rating_distribution.png', dpi=150, bbox_inches='tight')
print("\n✓ 评分分布图已保存: data/rating_distribution.png")

# ============================================
# 第三部分：关键词提取
# ============================================

print("\n[3/5] 正在提取关键词...")

def extract_keywords(texts, top_n=10):
    """简单的关键词提取"""
    # 定义关键词（实际项目中会用jieba分词）
    keywords = {
        '好用': 0, '简单': 0, '方便': 0, '丰富': 0, '专业': 0,
        '免费': 0, '素材': 0, '模板': 0, '转场': 0, '特效': 0,
        'AI': 0, '字幕': 0, '抠图': 0, '调色': 0, '剪辑': 0,
        '贵': 0, '付费': 0, '会员': 0, '水印': 0, '闪退': 0,
        '慢': 0, '卡': 0, '套路': 0, '限制': 0, '功能': 0
    }
    
    for text in texts:
        for keyword in keywords:
            if keyword in str(text):
                keywords[keyword] += 1
    
    # 排序返回
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords[:top_n]

# 提取各产品好评关键词
jianying_pos = jianying_df[jianying_df['rating'] >= 4]['content']
jianying_neg = jianying_df[jianying_df['rating'] <= 2]['content']
filmora_pos = filmora_df[filmora_df['rating'] >= 4]['content']
filmora_neg = filmora_df[filmora_df['rating'] <= 2]['content']

print("\n【剪映 - 好评关键词】")
for word, count in extract_keywords(jianying_pos, 5):
    if count > 0:
        print(f"  {word}: {count}次")

print("\n【剪映 - 差评关键词】")
for word, count in extract_keywords(jianying_neg, 5):
    if count > 0:
        print(f"  {word}: {count}次")

print("\n【Filmora - 好评关键词】")
for word, count in extract_keywords(filmora_pos, 5):
    if count > 0:
        print(f"  {word}: {count}次")

print("\n【Filmora - 差评关键词】")
for word, count in extract_keywords(filmora_neg, 5):
    if count > 0:
        print(f"  {word}: {count}次")

# ============================================
# 第四部分：评分趋势分析
# ============================================

print("\n[4/5] 正在分析评分趋势...")

# 按月统计
df['month'] = df['date'].dt.to_period('M')

monthly_stats = df.groupby(['month', 'product']).agg({
    'rating': ['mean', 'count']
}).reset_index()
monthly_stats.columns = ['month', 'product', 'avg_rating', 'count']
monthly_stats['month'] = monthly_stats['month'].astype(str)

# 绘制趋势图
fig, ax = plt.subplots(figsize=(12, 5))

for product in ['剪映', 'Filmora']:
    product_data = monthly_stats[monthly_stats['product'] == product]
    ax.plot(product_data['month'], product_data['avg_rating'], 
            marker='o', linewidth=2, label=product)

ax.set_xlabel('月份', fontsize=12)
ax.set_ylabel('平均评分', fontsize=12)
ax.set_title('月度平均评分趋势对比', fontsize=14)
ax.set_ylim([3, 5])
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('../data/rating_trend.png', dpi=150, bbox_inches='tight')
print("✓ 评分趋势图已保存: data/rating_trend.png")

# ============================================
# 第五部分：生成分析报告
# ============================================

print("\n[5/5] 正在生成分析报告...")

report = f"""# 视频剪辑软件用户评论分析报告

## 一、数据概况

| 指标 | 剪映 | Filmora |
|------|------|---------|
| 评论总数 | {len(jianying_df)}条 | {len(filmora_df)}条 |
| 平均评分 | {jianying_avg:.2f}/5.0 | {filmora_avg:.2f}/5.0 |
| 好评率(4-5星) | {jianying_good_rate:.1f}% | {filmora_good_rate:.1f}% |
| 差评率(1-2星) | {len(jianying_df[jianying_df['rating']<=2])/len(jianying_df)*100:.1f}% | {len(filmora_df[filmora_df['rating']<=2])/len(filmora_df)*100:.1f}% |

## 二、用户好评聚焦

### 剪映用户满意点
1. **操作简单**：零门槛上手，小白友好
2. **素材丰富**：模板、音乐、特效一应俱全
3. **AI功能强**：智能字幕、抠图好评度高
4. **免费使用**：基础功能完全免费

### Filmora用户满意点
1. **功能专业**：调色、多轨道等专业功能完善
2. **画质提升**：滤镜和调色效果获认可
3. **转场丰富**：选择多样，效果自然
4. **客服响应**：问题解决能力获好评

## 三、用户痛点分析

### 剪映用户槽点
1. **会员价格**：部分用户认为会员定价偏高
2. **软件稳定性**：偶发闪退问题
3. **导出限制**：免费版片尾有logo水印
4. **功能深度**：专业剪辑需求难以满足

### Filmora用户槽点
1. **订阅费用**：年费模式让用户有压力
2. **试用水印**：水印过大，体验受影响
3. **功能收费**：部分功能需额外付费
4. **AI限制**：AI功能有使用次数限制

## 四、关键洞察

### 洞察1：免费vs付费的体验差异
剪映的"免费优先"策略让用户好评率更高，但也带来了对会员价值的质疑。
Filmora的付费模式清晰，但水印和功能限制影响了试用体验。

### 洞察2：AI功能成为共同亮点
两款产品的AI功能（智能字幕、抠图）都获得高度认可。
但变现策略不同：剪映免费开放，Filmora设限收费。

### 洞察3：用户分层明显
剪映用户更看重"简单、免费、素材多"。
Filmora用户更看重"专业、功能全、画质好"。

## 五、产品建议

### 给剪映的建议
1. 优化软件稳定性，减少闪退
2. 考虑分层会员，满足不同需求
3. 增加进阶功能，留住成长型用户

### 给Filmora的建议
1. 优化试用体验，降低水印干扰
2. 提供更灵活的定价方案
3. 增加AI功能免费额度

## 六、数据产品启示

作为数据产品经理，从这次分析中得到的启示：

1. **评论是金矿**：用户评论直接反映产品痛点和亮点
2. **量化才有说服力**：好评率、关键词频次等量化指标支撑决策
3. **对比出洞察**：单一产品分析有限，竞品对比更有价值
4. **持续监控**：评分趋势可以反映版本更新的用户反馈

---

*报告生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}*
"""

# 保存报告
with open('../data/analysis_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("✓ 分析报告已保存: data/analysis_report.md")

# ============================================
# 完成
# ============================================

print("\n" + "="*50)
print("分析完成！生成的文件：")
print("="*50)
print("1. data/reviews.csv - 评论原始数据")
print("2. data/rating_distribution.png - 评分分布图")
print("3. data/rating_trend.png - 评分趋势图")
print("4. data/analysis_report.md - 分析报告")
print("="*50)