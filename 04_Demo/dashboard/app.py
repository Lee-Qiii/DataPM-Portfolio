import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta, datetime

st.set_page_config(page_title="数据看板", page_icon="📊", layout="wide")

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
current_date = datetime.now().strftime("%Y-%m-%d")

st.markdown("""
<style>
    .section-header {font-size: 20px; font-weight: 600; margin: 20px 0 15px 0; padding-bottom: 8px; border-bottom: 2px solid #667eea;}
    .alert-box {padding: 16px; border-radius: 10px; margin-bottom: 12px;}
    .alert-danger {background: #fee2e2; border-left: 5px solid #dc2626;}
    .alert-danger strong {color: #7f1d1d; font-size: 16px; font-weight: 700;}
    .alert-danger small {color: #991b1b; font-size: 14px; line-height: 1.8; font-weight: 500;}
    .alert-warning {background: #fef3c7; border-left: 5px solid #d97706;}
    .alert-warning strong {color: #78350f; font-size: 16px; font-weight: 700;}
    .alert-warning small {color: #92400e; font-size: 14px; line-height: 1.8; font-weight: 500;}
    .alert-success {background: #d1fae5; border-left: 5px solid #059669;}
    .alert-success strong {color: #064e3b; font-size: 16px; font-weight: 700;}
    .alert-success small {color: #065f46; font-size: 14px; line-height: 1.8; font-weight: 500;}
    .summary-box {background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 18px; border-radius: 10px; border: 1px solid #e2e8f0; margin: 15px 0;}
    .summary-title {font-weight: 700; color: #1e293b; margin-bottom: 12px; font-size: 16px;}
    .summary-item {color: #334155; font-size: 14px; margin: 6px 0; font-weight: 500;}
    .update-time {background: #f0fdf4; padding: 8px 12px; border-radius: 6px; font-size: 12px; color: #166534; display: inline-block; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    np.random.seed(42)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=364)
    dates = pd.date_range(start=start_date, end=end_date)
    n = len(dates)
    
    products = ['剪映', 'Filmora', 'CapCut']
    platforms = ['iOS', 'Android', 'Windows', 'Mac']
    regions = ['中国大陆', '北美', '欧洲', '东南亚', '其他']
    
    data_list = []
    
    for product in products:
        for platform in platforms:
            for region in regions:
                np.random.seed(hash(f"{product}{platform}{region}") % 2**32)
                
                if product == '剪映':
                    base_dau, base_new, base_retention, base_revenue = 180000, 6000, 0.47, 55000
                elif product == 'Filmora':
                    base_dau, base_new, base_retention, base_revenue = 120000, 4000, 0.44, 85000
                else:
                    base_dau, base_new, base_retention, base_revenue = 200000, 7500, 0.46, 45000
                
                plat_mult = {'iOS': 1.2, 'Android': 1.5, 'Windows': 0.8, 'Mac': 0.5}[platform]
                reg_mult = {'中国大陆': 1.8, '北美': 1.2, '欧洲': 1.0, '东南亚': 0.7, '其他': 0.3}[region]
                
                trend = np.linspace(0, 0.3, n)
                weekly = 0.1 * np.sin(np.linspace(0, 52*2*np.pi, n))
                noise = np.random.normal(0, 0.05, n)
                mult = (1 + trend + weekly + noise) * plat_mult * reg_mult
                
                dau = (base_dau * mult).astype(int)
                new_users = (base_new * mult * 0.8).astype(int)
                retention_d1 = np.clip(base_retention + np.random.normal(0, 0.02, n), 0.38, 0.55)
                retention_d7 = np.clip(retention_d1 * 0.58 + np.random.normal(0, 0.01, n), 0.20, 0.35)
                revenue = (base_revenue * mult * 0.9).astype(int)
                ai_usage = (dau * np.clip(0.35 + np.random.normal(0, 0.05, n), 0.25, 0.50)).astype(int)
                export_success = np.clip(0.94 + np.random.normal(0, 0.01, n), 0.88, 0.98)
                
                for i, date in enumerate(dates):
                    data_list.append({
                        'date': date,
                        'product': product,
                        'platform': platform,
                        'region': region,
                        'dau': max(dau[i], 1000),
                        'new_users': max(new_users[i], 100),
                        'retention_d1': retention_d1[i],
                        'retention_d7': retention_d7[i],
                        'revenue': max(revenue[i], 1000),
                        'ai_usage': max(ai_usage[i], 500),
                        'export_success': export_success[i]
                    })
    
    return pd.DataFrame(data_list)

df = load_data()

def format_num(num):
    if num >= 1000000:
        return f"{num/1000000:.2f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return f"{int(num):,}"

def calc_change(curr_val, prev_val):
    if prev_val == 0:
        return 0
    return (curr_val - prev_val) / prev_val * 100
with st.sidebar:
    st.markdown("## 🎬 数据看板")
    st.markdown("---")
    
    st.markdown("### 📅 时间范围")
    time_map = {"今日": 1, "近7天": 7, "近14天": 14, "近30天": 30, "近60天": 60, "近90天": 90}
    time_range = st.selectbox("选择时间", list(time_map.keys()), index=3, label_visibility="collapsed")
    days = time_map[time_range]
    
    st.markdown("### 🏷️ 数据筛选")
    product_options = ["全部产品"] + list(df['product'].unique())
    product = st.selectbox("产品", product_options, index=0)
    
    platform_options = ["全部平台"] + list(df['platform'].unique())
    platform = st.selectbox("平台", platform_options, index=0)
    
    region_options = ["全部地区"] + list(df['region'].unique())
    region = st.selectbox("地区", region_options, index=0)
    
    st.markdown("---")
    st.markdown("### ⚙️ 显示设置")
    show_target = st.checkbox("显示目标线", value=True)
    show_avg = st.checkbox("显示均值线", value=True)
    
    st.markdown("---")
    st.markdown(f"""
    <div class="update-time">
        🕐 更新时间<br>
        <strong>{current_time}</strong>
    </div>
    """, unsafe_allow_html=True)
    st.caption("📡 数据延迟: T+1")

end_date = df['date'].max()
start_date = end_date - timedelta(days=days-1)

filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
if product != "全部产品":
    filtered = filtered[filtered['product'] == product]
if platform != "全部平台":
    filtered = filtered[filtered['platform'] == platform]
if region != "全部地区":
    filtered = filtered[filtered['region'] == region]

daily = filtered.groupby('date').agg({
    'dau': 'sum', 'new_users': 'sum', 'retention_d1': 'mean',
    'retention_d7': 'mean', 'revenue': 'sum', 'ai_usage': 'sum', 'export_success': 'mean'
}).reset_index()

prev_end = start_date - timedelta(days=1)
prev_start = prev_end - timedelta(days=days-1)
prev_filtered = df[(df['date'] >= prev_start) & (df['date'] <= prev_end)].copy()
if product != "全部产品":
    prev_filtered = prev_filtered[prev_filtered['product'] == product]
if platform != "全部平台":
    prev_filtered = prev_filtered[prev_filtered['platform'] == platform]
if region != "全部地区":
    prev_filtered = prev_filtered[prev_filtered['region'] == region]

curr_avg = daily.mean(numeric_only=True)
prev_avg = prev_filtered.groupby('date').agg({
    'dau': 'sum', 'new_users': 'sum', 'retention_d1': 'mean',
    'retention_d7': 'mean', 'revenue': 'sum', 'ai_usage': 'sum', 'export_success': 'mean'
}).mean(numeric_only=True) if len(prev_filtered) > 0 else curr_avg

filter_desc = []
filter_desc.append(product if product != "全部产品" else "全部产品")
filter_desc.append(platform if platform != "全部平台" else "全部平台")
filter_desc.append(region if region != "全部地区" else "全部地区")

st.title("📊 视频剪辑软件数据看板")
st.caption(f"📅 {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')} ({days}天) | 🏷️ {' · '.join(filter_desc)} | 🕐 {current_time}")

col_refresh, col_space = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")
st.markdown('<p class="section-header">🎯 核心指标</p>', unsafe_allow_html=True)

period_dau_change = calc_change(curr_avg['dau'], prev_avg['dau'])
period_new_change = calc_change(curr_avg['new_users'], prev_avg['new_users'])
period_ret_change = (curr_avg['retention_d1'] - prev_avg['retention_d1']) * 100
period_rev_change = calc_change(curr_avg['revenue'], prev_avg['revenue'])
period_ai_change = calc_change(curr_avg['ai_usage'], prev_avg['ai_usage'])
period_exp_change = (curr_avg['export_success'] - prev_avg['export_success']) * 100

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("DAU (日均)", format_num(curr_avg['dau']), f"{period_dau_change:+.1f}%")
m2.metric("新增 (日均)", format_num(curr_avg['new_users']), f"{period_new_change:+.1f}%")
m3.metric("次日留存", f"{curr_avg['retention_d1']*100:.1f}%", f"{period_ret_change:+.2f}%")
m4.metric("收入 (日均)", f"¥{format_num(curr_avg['revenue'])}", f"{period_rev_change:+.1f}%")
m5.metric("AI使用 (日均)", format_num(curr_avg['ai_usage']), f"{period_ai_change:+.1f}%")
m6.metric("导出成功率", f"{curr_avg['export_success']*100:.1f}%", f"{period_exp_change:+.2f}%")

st.markdown(f"""
<div class="summary-box">
    <div class="summary-title">📊 {time_range}数据摘要 ({' · '.join(filter_desc)}) · 更新于 {current_time}</div>
    <div class="summary-item">• 累计活跃: <strong>{format_num(daily['dau'].sum())}</strong> 人次 | 日均: <strong>{format_num(curr_avg['dau'])}</strong></div>
    <div class="summary-item">• 累计新增: <strong>{format_num(daily['new_users'].sum())}</strong> 人 | 日均: <strong>{format_num(curr_avg['new_users'])}</strong></div>
    <div class="summary-item">• 累计收入: <strong>¥{format_num(daily['revenue'].sum())}</strong> | 日均: <strong>¥{format_num(curr_avg['revenue'])}</strong></div>
    <div class="summary-item">• 累计AI调用: <strong>{format_num(daily['ai_usage'].sum())}</strong> 次 | 渗透率: <strong>{curr_avg['ai_usage']/max(curr_avg['dau'],1)*100:.1f}%</strong></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p class="section-header">📈 趋势分析</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["👥 用户增长", "🔄 留存分析", "🤖 AI功能", "💰 收入分析"])
with tab1:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily['date'], y=daily['dau'], mode='lines', name='DAU',
                                  line=dict(color='#667eea', width=2.5), fill='tozeroy', fillcolor='rgba(102,126,234,0.1)'))
        if show_avg:
            fig.add_hline(y=curr_avg['dau'], line_dash="dot", line_color="#10b981", annotation_text=f"均值: {format_num(curr_avg['dau'])}")
        fig.update_layout(title=f'DAU趋势 ({time_range})', height=360, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with r1c2:
        colors = ['#10b981' if x >= curr_avg['new_users'] else '#94a3b8' for x in daily['new_users']]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=daily['date'], y=daily['new_users'], marker_color=colors))
        if show_avg:
            fig.add_hline(y=curr_avg['new_users'], line_dash="dot", line_color="#667eea", annotation_text=f"均值: {format_num(curr_avg['new_users'])}")
        fig.update_layout(title=f'每日新增 ({time_range})', height=360, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    if product == "全部产品":
        st.markdown("##### 📊 分产品数据")
        prod_data = filtered.groupby('product').agg({'dau': 'sum', 'new_users': 'sum', 'revenue': 'sum'}).reset_index()
        prod_data.columns = ['产品', 'DAU(累计)', '新增(累计)', '收入(累计)']
        prod_data['DAU(累计)'] = prod_data['DAU(累计)'].apply(format_num)
        prod_data['新增(累计)'] = prod_data['新增(累计)'].apply(format_num)
        prod_data['收入(累计)'] = prod_data['收入(累计)'].apply(lambda x: f"¥{format_num(x)}")
        st.dataframe(prod_data, use_container_width=True, hide_index=True)

with tab2:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily['date'], y=daily['retention_d1']*100, mode='lines+markers', name='次日留存', line=dict(color='#667eea', width=2)))
        fig.add_trace(go.Scatter(x=daily['date'], y=daily['retention_d7']*100, mode='lines+markers', name='7日留存', line=dict(color='#10b981', width=2)))
        if show_target:
            fig.add_hline(y=46, line_dash="dash", line_color="#ef4444", annotation_text="目标: 46%")
        fig.update_layout(title=f'留存趋势 ({time_range})', height=360, yaxis=dict(range=[15, 55]), legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fig, use_container_width=True)
    with r1c2:
        funnel = pd.DataFrame({'天数': ['D1', 'D3', 'D7', 'D14', 'D30'], 
                               '留存率': [curr_avg['retention_d1']*100, curr_avg['retention_d1']*82, curr_avg['retention_d7']*100, curr_avg['retention_d7']*78, curr_avg['retention_d7']*65]})
        fig = px.bar(funnel, x='天数', y='留存率', text='留存率', color='留存率', color_continuous_scale='Blues')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(title='留存漏斗', height=360, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily['date'], y=daily['ai_usage'], mode='lines', line=dict(color='#8b5cf6', width=2.5), fill='tozeroy', fillcolor='rgba(139,92,246,0.1)'))
        if show_avg:
            fig.add_hline(y=curr_avg['ai_usage'], line_dash="dot", line_color="#10b981", annotation_text=f"均值: {format_num(curr_avg['ai_usage'])}")
        fig.update_layout(title=f'AI使用趋势 ({time_range})', height=360, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with r1c2:
        ai_data = pd.DataFrame({
            '功能': ['AI字幕', 'AI抠图', 'AI降噪', 'AI配乐', 'AI封面'],
            '使用量': [int(curr_avg['ai_usage']*0.40), int(curr_avg['ai_usage']*0.28), int(curr_avg['ai_usage']*0.16), int(curr_avg['ai_usage']*0.10), int(curr_avg['ai_usage']*0.06)]
        }).sort_values('使用量')
        fig = px.bar(ai_data, y='功能', x='使用量', orientation='h', text='使用量', color='使用量', color_continuous_scale='Purples')
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(title='AI功能排行', height=360, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
    ai1, ai2, ai3, ai4 = st.columns(4)
    ai_pen = curr_avg['ai_usage'] / max(curr_avg['dau'], 1) * 100
    ai1.metric("AI渗透率", f"{ai_pen:.1f}%", f"{period_ai_change/5:+.1f}%")
    ai2.metric("字幕准确率", "96.8%", "+0.3%")
    ai3.metric("人均调用", f"{curr_avg['ai_usage']/max(curr_avg['dau']/3,1):.1f}次", "+0.2")
    ai4.metric("满意度", "4.7/5", "+0.1")

with tab4:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily['date'], y=daily['revenue'], mode='lines', line=dict(color='#f59e0b', width=2.5), fill='tozeroy', fillcolor='rgba(245,158,11,0.1)'))
        if show_avg:
            fig.add_hline(y=curr_avg['revenue'], line_dash="dot", line_color="#10b981", annotation_text=f"均值: ¥{format_num(curr_avg['revenue'])}")
        fig.update_layout(title=f'收入趋势 ({time_range})', height=360, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with r1c2:
        pay = pd.DataFrame({
            '类型': ['月度会员', '年度会员', '永久版', '素材包', 'AI额度'],
            '收入': [int(curr_avg['revenue']*0.40), int(curr_avg['revenue']*0.32), int(curr_avg['revenue']*0.15), int(curr_avg['revenue']*0.08), int(curr_avg['revenue']*0.05)]
        })
        fig = px.pie(pay, values='收入', names='类型', title='收入构成', hole=0.4, color_discrete_sequence=['#667eea', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'])
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    p1, p2, p3, p4 = st.columns(4)
    arpu = curr_avg['revenue'] / max(curr_avg['dau'], 1)
    p1.metric("付费转化", f"{curr_avg['revenue']/max(curr_avg['dau']*50,1)*100:.2f}%", f"{period_rev_change/10:+.2f}%")
    p2.metric("ARPU", f"¥{arpu:.2f}", f"{period_rev_change/20:+.2f}")
    p3.metric("ARPPU", f"¥{arpu*35:.1f}", f"+¥{abs(period_rev_change/5):.1f}")
    p4.metric("累计收入", f"¥{format_num(daily['revenue'].sum())}", f"{period_rev_change:+.1f}%")

st.markdown("---")
st.markdown('<p class="section-header">⚠️ 数据预警</p>', unsafe_allow_html=True)

target_retention, target_new, target_export = 0.46, 18000 * (1 if product == "全部产品" else 0.35), 0.95

ret_val = curr_avg['retention_d1']
ret_status = "alert-success" if ret_val >= target_retention else "alert-warning" if ret_val >= target_retention * 0.95 else "alert-danger"
ret_icon = "✅" if ret_val >= target_retention else "⚠️" if ret_val >= target_retention * 0.95 else "🚨"
ret_title = "留存达标" if ret_val >= target_retention else "留存预警" if ret_val >= target_retention * 0.95 else "留存告警"

new_val = curr_avg['new_users']
new_status = "alert-success" if new_val >= target_new else "alert-warning" if new_val >= target_new * 0.85 else "alert-danger"
new_icon = "✅" if new_val >= target_new else "⚠️" if new_val >= target_new * 0.85 else "🚨"
new_title = "新增达标" if new_val >= target_new else "新增预警" if new_val >= target_new * 0.85 else "新增告警"

exp_val = curr_avg['export_success']
exp_status = "alert-success" if exp_val >= target_export else "alert-warning" if exp_val >= target_export * 0.98 else "alert-danger"
exp_icon = "✅" if exp_val >= target_export else "⚠️" if exp_val >= target_export * 0.98 else "🚨"
exp_title = "导出正常" if exp_val >= target_export else "导出预警" if exp_val >= target_export * 0.98 else "导出告警"

ai_growth = period_ai_change
ai_status = "alert-success" if ai_growth > 0 else "alert-warning" if ai_growth > -5 else "alert-danger"
ai_icon = "✅" if ai_growth > 0 else "⚠️" if ai_growth > -5 else "🚨"
ai_title = "AI增长" if ai_growth > 0 else "AI持平" if ai_growth > -5 else "AI下降"

a1, a2, a3, a4 = st.columns(4)
with a1:
    st.markdown(f'''<div class="alert-box {ret_status}"><strong>{ret_icon} {ret_title}</strong><br><small>当前: {ret_val*100:.1f}% | 目标: {target_retention*100:.0f}%<br>差距: {(ret_val-target_retention)*100:+.1f}% | 环比: {period_ret_change:+.2f}%</small></div>''', unsafe_allow_html=True)
with a2:
    st.markdown(f'''<div class="alert-box {new_status}"><strong>{new_icon} {new_title}</strong><br><small>日均: {format_num(new_val)} | 目标: {format_num(target_new)}<br>达成: {new_val/target_new*100:.0f}% | 环比: {period_new_change:+.1f}%</small></div>''', unsafe_allow_html=True)
with a3:
    st.markdown(f'''<div class="alert-box {exp_status}"><strong>{exp_icon} {exp_title}</strong><br><small>成功率: {exp_val*100:.1f}% | 目标: {target_export*100:.0f}%<br>差距: {(exp_val-target_export)*100:+.1f}% | 环比: {period_exp_change:+.2f}%</small></div>''', unsafe_allow_html=True)
with a4:
    st.markdown(f'''<div class="alert-box {ai_status}"><strong>{ai_icon} {ai_title}</strong><br><small>日均: {format_num(curr_avg['ai_usage'])}次<br>渗透率: {curr_avg['ai_usage']/max(curr_avg['dau'],1)*100:.1f}% | 环比: {ai_growth:+.1f}%</small></div>''', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p class="section-header">📋 数据明细</p>', unsafe_allow_html=True)

with st.expander(f"📊 查看{time_range}详细数据 ({' · '.join(filter_desc)})", expanded=False):
    show = daily[['date', 'dau', 'new_users', 'retention_d1', 'retention_d7', 'revenue', 'ai_usage']].copy()
    show.columns = ['日期', 'DAU', '新增', '次日留存', '7日留存', '收入', 'AI使用']
    show['日期'] = show['日期'].dt.strftime('%Y-%m-%d')
    show['DAU'] = show['DAU'].apply(lambda x: f"{int(x):,}")
    show['新增'] = show['新增'].apply(lambda x: f"{int(x):,}")
    show['次日留存'] = (show['次日留存'] * 100).round(1).astype(str) + '%'
    show['7日留存'] = (show['7日留存'] * 100).round(1).astype(str) + '%'
    show['收入'] = show['收入'].apply(lambda x: f"¥{int(x):,}")
    show['AI使用'] = show['AI使用'].apply(lambda x: f"{int(x):,}")
    st.dataframe(show, use_container_width=True, hide_index=True)

btn1, btn2, btn3, btn4 = st.columns([1, 1, 1, 3])
file_name = f"data_{product}_{platform}_{region}_{time_range}".replace(" ", "_").replace("全部", "all")
btn1.download_button("📥 导出CSV", daily.to_csv(index=False).encode('utf-8-sig'), f"{file_name}.csv", use_container_width=True)

report_content = f"""# {time_range}数据报告
生成时间: {current_time}

## 筛选条件
- 产品: {product}
- 平台: {platform}
- 地区: {region}
- 时间: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}

## 核心指标
- DAU日均: {format_num(curr_avg['dau'])} (环比: {period_dau_change:+.1f}%)
- 新增日均: {format_num(curr_avg['new_users'])} (环比: {period_new_change:+.1f}%)
- 次日留存: {curr_avg['retention_d1']*100:.1f}% (环比: {period_ret_change:+.2f}%)
- 收入日均: ¥{format_num(curr_avg['revenue'])} (环比: {period_rev_change:+.1f}%)
"""
btn2.download_button("📥 导出报告", report_content, f"{file_name}_report.md", use_container_width=True)

st.markdown("---")
st.caption(f"📊 数据看板 | {time_range} | {' · '.join(filter_desc)} | 更新时间: {current_time} | 数据产品经理作品集")