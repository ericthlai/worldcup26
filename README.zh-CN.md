[English](README.md) · **简体中文**

# 世界杯 2026 观赛手册 ⚽

一个手机优先的世界杯 2026 预测小应用 —— 湾区 / 美国境内场次视角。给小组排名次、推演淘汰赛对阵图，还能看来自真实预测市场的实时胜率。

**▶ 开始玩：**
- 🇨🇳 中文 —— https://ericthlai.github.io/worldcup26/
- 🇬🇧 English —— https://ericthlai.github.io/worldcup26/en/

> 打开就能用，所有选择自动存在你自己的浏览器里。无需登录，不上传任何信息。纯属娱乐。

## 功能
- **赛程** —— 美国境内全部 52 场小组赛，每场带一条来自 [Polymarket](https://polymarket.com) 预测市场的实时**胜 / 平 / 胜**概率条
- **小组** —— 点击球队排名次；前 2 名晋级，第 3 名进入「最佳第 3」候选池
- **对阵** —— 可交互的淘汰赛对阵图，从小组排名自动带入，外加实时**夺冠概率榜**
- **分享** —— 一键生成可分享的预测卡片图

## 技术
单页静态网页，无需构建：[Preact](https://preactjs.com) + [HTM](https://github.com/developit/htm) 本地引入，预测存在 `localStorage`，实时胜率由浏览器直接调用 Polymarket 公开的 Gamma API。托管在 GitHub Pages（免费）。

英文版（`/en/`）和中文版（`/`）共用同一套逻辑与同一份预测存档；页脚链接可互相切换。

## 本地运行
```bash
python -m http.server 8000
# 然后打开 http://localhost:8000
```

## 免责声明
开球时间以 FIFA 官方 App 为准。这里的百分比是 Polymarket 博彩市场的*隐含概率*，仅供娱乐。
