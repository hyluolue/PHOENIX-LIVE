// Phoenix 品牌战略 V1 全部 32 条原文（从 React bundle 抽出）
// 区域: BD=孟加拉 / ID=印尼
// quadrant: A=战略与定位周复盘 / B=差异化与执行
const V1_STRATEGIES = [
  // ============ A. 战略与定位周复盘 - BD (12 条) ============
  { id: 1, region: 'bd', quadrant: 'A', framework: 'STP+第一性原理', label: '品牌第一性原理 (Brand First Principle)', priority: 3,
    title: 'BD 凤凰 = 中高端 MTB 安全认证第一品牌',
    body: '核心：骑行安全 = 骑行自由 = SGS 认证不是口号。Brand Promise = "Safety Certified MTB"。',
    kpi: '孟加拉 MTB 品类无提示认知率 >10%（6 个月）' },

  { id: 2, region: 'bd', quadrant: 'A', framework: '飞轮', label: '增长飞轮 (Growth Flywheel)', priority: 2,
    title: 'BD 飞轮：KOL 信任→社群留存→Daraz 转化→口碑裂变→俱乐部',
    body: 'MTB 俱乐部 KOL 内容（信任）→ Facebook 社群（留存）→ Daraz 购买（转化）→ 口碑分享（裂变）→ 俱乐部赞助（扩大）→ 新用户社群',
    kpi: 'MTB 俱乐部合作 >3 个（12 个月）' },

  { id: 3, region: 'bd', quadrant: 'A', framework: '4P+凡勃伦', label: '凡勃伦效应 (Veblen Effect)', priority: 1,
    title: 'Tornado Elite BDT 28,000 定位高端',
    body: '"通过 SGS 认证的最安全铝合金 MTB" = 物超所值。Trek/Giant 太贵，凤凰是最佳性价比高端选择。',
    kpi: '高端 MTB 款占品 >15%（销量）' },

  { id: 4, region: 'bd', quadrant: 'A', framework: '4P+内容', label: '董氏文案四式 (Dong Copywriting 4)', priority: 2,
    title: 'BD 4 式文案：恐惧/对比/证言/数字',
    body: '①恐惧型：\'孟加拉山地骑行，车架断裂不是故事\' ②对比型：\'普通刹 vs 凤凰液压碟刹\' ③证言型：MTB 俱乐部 KOL 实测 ④数字型：SGS 认证 120kg 承载测试',
    kpi: 'MTB 安全视频播放量 >20 万（孟加拉）' },

  { id: 5, region: 'bd', quadrant: 'A', framework: '品牌资产', label: '护城河 (Moat)', priority: 3,
    title: 'BD 护城河：SGS+BSTI+俱乐部',
    body: '凤凰护城河：SGS 认证（技术壁垒，孟加拉唯一）+ BSTI 认证（监管壁垒）+ MTB 俱乐部赞助（社群壁垒）。Veloce/Core 无法快速复制。',
    kpi: 'SGS+BSTI 双认证领先竞品至少 6 个月' },

  { id: 6, region: 'bd', quadrant: 'A', framework: 'STP+第一性原理', label: '第一性原理链 (First Principle Chain)', priority: 3,
    title: 'BD 第一性原理：骑行本质=探索自由',
    body: '骑行本质：探索自由 → 核心需求：中高端 MTB + 骑行安全 → 差异化：SGS 认证安全 MTB → 定位：孟加拉最安全的中高端 MTB',
    kpi: '\'安全 MTB\' 关键词占据率 >50%' },

  { id: 7, region: 'bd', quadrant: 'A', framework: 'STP', label: '聚焦策略 (Focus Strategy)', priority: 3,
    title: 'BD 聚焦 26-29 寸中高端',
    body: '孟加拉：聚焦 26-29 寸 MTB 中高端市场（BDT 14,000-32,000），不做低价通勤/童车。all-in \'认证安全 MTB\' 心智。',
    kpi: 'MTB 中高端市场份额 >12%（12 个月）' },

  { id: 8, region: 'bd', quadrant: 'A', framework: '飞轮', label: '圈层商业 (Circle Commerce)', priority: 2,
    title: 'BD 圈层：俱乐部赞助→会员体系→配件复购',
    body: '达卡/吉大港 MTB 俱乐部 → 俱乐部赞助/试用 → KOL 测评内容 → 社群传播 → 凤凰会员体系 → 配件复购升级',
    kpi: 'MTB 俱乐部会员转化率 >8%' },

  { id: 9, region: 'bd', quadrant: 'A', framework: 'STP+洞察', label: '洞察人性 (Human Insight)', priority: 1,
    title: 'BD 骑手渴望：去更远+装备够安全',
    body: '孟加拉 MTB 骑行者核心渴望：\'我能去更远的地方\' + \'我的装备够安全\'。次级渴望：\'我的车比朋友的更...\'。核心恐惧：\'车架在山地断\' + \'刹不住车\'。',
    kpi: 'MTB 安全内容互动率 >7%' },

  { id: 10, region: 'bd', quadrant: 'A', framework: '4P', label: 'KANO 模型 (KANO Model)', priority: 1,
    title: 'BD 产品必备/渴望分层',
    body: '必备型（Must-be）：车架强度/刹车安全/认证 + SGS 五维安全。渴望型（Attractive）：碳纤维轻量化/30 速变速/个性化颜色 → Tornado Elite。',
    kpi: '必备安全功能 100% 达标' },

  { id: 11, region: 'bd', quadrant: 'A', framework: 'STP', label: '竞品失语症 (Competitor Silence)', priority: 3,
    title: 'BD 竞品不打认证 MTB = 凤凰机会',
    body: 'Veloce/Core/Avon 不打 \'安全认证 MTB\' → 凤凰立即占领这个认知空白。孟加拉无一家中高端 MTB 品牌主打 SGS 认证。',
    kpi: '\'认证 MTB\' 孟加拉搜索排名 Top1' },

  { id: 12, region: 'bd', quadrant: 'A', framework: '洞察', label: 'Kahneman 快与慢 (Nudge)', priority: 1,
    title: 'BD 内容结构：情绪→理性',
    body: '孟加拉 MTB 骑手情绪脑（追求冒险自由）强于理性脑（算价格）。内容以 \'山地探索故事\' 开头，理性证明（SGS 数据）在结尾。',
    kpi: '视频完播率 >45%' },

  // ============ A. 战略与定位周复盘 - ID (4 条) ============
  { id: 13, region: 'id', quadrant: 'A', framework: '品牌资产', label: '认证安全战略 (Certified Safety Strategy)', priority: 3,
    title: 'ID 核心战略：认证+文化+UCI 三层',
    body: '【核心】凤凰不打价格战，不做大牌平替。战略：\'用认证标准甩开白牌，用文化故事与高端品牌差异化\'。认证层：凤凰全系 SGS+SNI 双认证（白牌无法突破）；文化层：百年民族品牌+华人情感共鸣（高端品牌不做的）；产品层：UCI 认证公路车（专业竞技壁垒）。品牌核心文案：\'骑行安全，始于认证\'。',
    kpi: 'SGS/SNI 认证成为印尼 MTB 品类安全标准代名词（12 个月）' },

  { id: 14, region: 'id', quadrant: 'A', framework: '4P+UCI', label: 'UCI 车架研发战略 (UCI Frame R&D Roadmap)', priority: 3,
    title: 'ID UCI 车架：每年 1 款，覆盖 3 品类',
    body: 'UCI 认证车架为核心卖点；公路车销量占比 >20%（12 个月）；公路车俱乐部合作 >3 个。每年推出 >1 款 UCI 认证新品；UCI 认证产品线覆盖 >3 个细分品类。',
    kpi: '公路车销量 >20%' },

  { id: 15, region: 'id', quadrant: 'A', framework: 'STP', label: '聚焦策略 (Focus Strategy)', priority: 3,
    title: 'ID 聚焦 27.5-29 寸 Rp 8-18M',
    body: '印尼：聚焦 27.5-29 寸 MTB 中高端市场（Rp 8-18M），不做低端/童车。all-in \'SGS+SNI 双认证安全 MTB\'。对标 Polygon Xtrada5（Rp 6.6M）高一个档次。',
    kpi: '中高端 MTB 市场份额 >10%（18 个月）' },

  { id: 16, region: 'id', quadrant: 'A', framework: '飞轮', label: '圈层商业 (Circle Commerce)', priority: 2,
    title: 'ID 圈层：Strava 团体→配件生态',
    body: 'Strava Indonesia 骑行团体 → KOL 测评内容 → 凤凰 MTB 试用 → 会员积分体系 → 配件生态（把立/链条/车胎）→ 公路车升级',
    kpi: '俱乐部会员数 >3000（12 个月）' },

  // ============ B. 差异化与执行 - BD (8 条) ============
  { id: 17, region: 'bd', quadrant: 'B', framework: 'STP', label: '竞品地图 (Competitor Map)', priority: 3,
    title: 'BD 14 品牌竞品地图',
    body: '竞品：phoenix / marine / giant / foxter / pacific / warrior / thorne / duranta / veloce / be worth / polygon ... 详见 Daraz 数据（74 条商品 / 9 品牌）',
    kpi: '竞品价格战月报' },

  { id: 18, region: 'bd', quadrant: 'B', framework: '4P', label: 'SKU 矩阵 - Tornado Elite', priority: 3,
    title: 'Tornado Elite 27.5/29 寸 24.5K+',
    body: '27.5/29 寸 MTB 旗舰款，BDT 24,500-30,000+，6061 铝合金，SGS+RoHS+UCI 认证，目标=BD 中高端 MTB 玩家/竞赛家庭',
    kpi: '中高端 MTB 销量' },

  { id: 19, region: 'bd', quadrant: 'B', framework: '4P', label: 'SKU 矩阵 - Thunder', priority: 3,
    title: 'Thunder 26/29 寸 BDT 16.8-22K',
    body: '26/29 寸 MTB 中高端，BDT 16,800-22,000，6061 铝合金，21-24 速，SGS 认证，目标=BD MTB 中端玩家/竞赛家庭',
    kpi: '中端 MTB 销量' },

  { id: 20, region: 'bd', quadrant: 'B', framework: '4P', label: 'SKU 矩阵 - Commuter Pro', priority: 3,
    title: 'Commuter Pro 700C 12.8-16.5K',
    body: '700C 城市通勤车，BDT 12,800-16,500，铝合金，7-21 速，SGS+RoHS+UCI 认证，目标=BD 城市通勤者',
    kpi: '中端 MTB 销量' },

  { id: 21, region: 'bd', quadrant: 'B', framework: '4P', label: 'KANO 模型', priority: 1,
    title: 'BD KANO 必/渴望分层',
    body: '必备：车架强度/刹车/认证/SGS 五维安全。渴望：碳纤维/30 速/个性化颜色 → Tornado Elite。',
    kpi: '必备 100% 达标' },

  { id: 22, region: 'bd', quadrant: 'B', framework: '洞察', label: '洞察人性', priority: 1,
    title: 'BD 骑手渴望+恐惧',
    body: '核心渴望：\'我能去更远的地方\' + \'我的装备够安全\'。核心恐惧：\'车架在山地断\' + \'刹不住车\'。',
    kpi: 'MTB 安全内容互动 >7%' },

  { id: 23, region: 'bd', quadrant: 'B', framework: '4P', label: '诚实定位 (Honest Positioning)', priority: 3,
    title: '诚实定位 = 品牌哲学',
    body: '诚实定位 = 品牌哲学（叙事基调，非分析工具）',
    kpi: '心智占位' },

  { id: 24, region: 'bd', quadrant: 'B', framework: '品牌资产', label: '认知占有率', priority: 3,
    title: '\'最耐久 MTB\' 认知占有率 >40%',
    body: '⚠️ 这是 V1 唯一提到\'耐久\'的 KPI - 与你 Q3 答案（耐久=心智资产）一致',
    kpi: '耐久认知占有率 >40%（12 个月）' },

  // ============ B. 差异化与执行 - ID (8 条) ============
  { id: 25, region: 'id', quadrant: 'B', framework: '4P+凡勃伦', label: '凡勃伦效应', priority: 1,
    title: 'Polygon Fighter Rp 15M 中端定位',
    body: '⚠️ Polygon Collossus Rp 100M 和 Giant Propel Rp 65M 占据顶端。凤凰 Polygon Fighter Rp 15M 定价中端 → 同场竞技的专业伙伴定位，而非廉价替代。',
    kpi: '中端 MTB 款占比 >25%' },

  { id: 26, region: 'id', quadrant: 'B', framework: '4P+内容', label: '董氏文案四式', priority: 2,
    title: 'ID 4 式文案',
    body: '①恐惧型：\'砾石路上刹车失灵，不是冒险是送命\' ②对比型：\'Polygon 原装 vs 凤凰液压碟刹\' ③证言型：Strava 印尼骑手测评 ④数字型：SNI+SGS 双认证',
    kpi: 'MTB 安全内容互动 >6%' },

  { id: 27, region: 'id', quadrant: 'B', framework: '品牌资产', label: '护城河', priority: 3,
    title: 'ID 护城河：SGS+SNI 双认证',
    body: '凤凰护城河：SGS+SNI 双认证（Polygon 仅有 SNI）+ 俱乐部赞助（社群壁垒）+ 探险骑行内容（KOL 壁垒）。Polygon 无 SGS 认证。',
    kpi: 'SGS+SNI 双认证领先 Polygon 至少 9 个月' },

  { id: 28, region: 'id', quadrant: 'B', framework: 'STP+第一性原理', label: '第一性原理链', priority: 3,
    title: 'ID 第一性原理：连接人与土地',
    body: '骑行本质：连接人与土地 → 核心需求：安全+性能+认证 → 差异化：SGS+SNI 双认证 MTB → 定位：印尼最安全的中高端 MTB（Polygon 无 SGS）',
    kpi: '\'安全 MTB\' 关键词印尼 Top3' },

  { id: 29, region: 'id', quadrant: 'B', framework: '4P', label: 'KANO 模型', priority: 1,
    title: 'ID KANO 必/渴望分层',
    body: '必备：车架强度/刹车/认证/SGS 五维。渴望：30 速/碳纤维/胎压监测 → Polygon Fighter。',
    kpi: '必备 100% 满足 SGS+SNI' },

  { id: 30, region: 'id', quadrant: 'B', framework: '洞察', label: '洞察人性', priority: 1,
    title: 'ID 骑手渴望+恐惧',
    body: '渴望：\'探索苏门答腊/爪哇的山\' + \'装备得到队友认可\'。恐惧：\'在偏远山路车架断\' + \'配件坏了找不到维修\'。',
    kpi: '印尼 MTB 安全内容互动 >6%' },

  { id: 31, region: 'id', quadrant: 'B', framework: '品牌资产', label: '认知占位', priority: 3,
    title: '安全认证联想度 Top3',
    body: '印尼市场：安全认证联想度 Top3',
    kpi: '联想度 Top3' },

  { id: 32, region: 'id', quadrant: 'B', framework: '品牌资产', label: '民族文化+华人情感共鸣', priority: 3,
    title: '文化层：百年民族品牌+华人情感',
    body: '高端品牌不做\'文化故事\'，凤凰做 = 差异化钩子',
    kpi: '印尼华人圈认知' },
];

// V1 框架归类（4 大框架：STP / 4P / 品牌资产 / 飞轮）
const V1_FRAMEWORK_MAP = {
  stp: { name: 'STP (Segmentation-Targeting-Positioning)', count: 7,
    items: [
      { id: 1, role: '定位', note: 'BD=中高端MTB安全认证第一品牌' },
      { id: 6, role: '定位链', note: 'BD 第一性原理链 → 定位' },
      { id: 7, role: '细分+目标', note: 'BD 聚焦 26-29 寸 BDT 14-32K' },
      { id: 11, role: '细分空白', note: 'BD 竞品不打认证 MTB' },
      { id: 15, role: '细分+目标', note: 'ID 聚焦 27.5-29 寸 Rp 8-18M' },
      { id: 17, role: '细分', note: 'BD 14 品牌竞品地图' },
      { id: 28, role: '定位链', note: 'ID 第一性原理链 → 定位' },
    ],
    gap: 'V1 缺少"基础代步→中端"过渡人群 STP 切片' },

  '4p': { name: '4P (Product/Price/Place/Promotion)', count: 9,
    items: [
      { id: 3, role: '价格/产品', note: 'BD Tornado Elite BDT 28K 凡勃伦' },
      { id: 4, role: '促销/内容', note: 'BD 董氏文案 4 式' },
      { id: 10, role: '产品分层', note: 'BD KANO 必备/渴望' },
      { id: 18, role: '产品 SKU', note: 'Tornado Elite 24.5K+' },
      { id: 19, role: '产品 SKU', note: 'Thunder 16.8-22K' },
      { id: 20, role: '产品 SKU', note: 'Commuter Pro 12.8-16.5K' },
      { id: 21, role: '产品分层', note: 'BD KANO 必/渴望' },
      { id: 25, role: '价格/产品', note: 'ID Polygon Fighter Rp 15M' },
      { id: 26, role: '促销/内容', note: 'ID 董氏文案 4 式' },
      { id: 29, role: '产品分层', note: 'ID KANO 必/渴望' },
    ],
    gap: '4P 没有显式映射到 STP 细分上。Commuter Pro 是入门通勤但 STP 没识别基础用户' },

  brand_assets: { name: '品牌资产 (Identity/Awareness/Loyalty/Association/Perceived Quality)', count: 8,
    items: [
      { id: 5, role: '感知质量', note: 'BD 护城河 SGS+BSTI' },
      { id: 13, role: '品牌资产/认知', note: 'ID 核心战略：认证+文化+UCI' },
      { id: 14, role: '品牌资产/UCI', note: 'ID UCI 车架研发' },
      { id: 23, role: '品牌哲学', note: '诚实定位 = 品牌哲学' },
      { id: 24, role: '认知', note: 'BD 耐久认知占有率 >40%' },
      { id: 27, role: '感知质量', note: 'ID 护城河 SGS+SNI' },
      { id: 31, role: '认知', note: 'ID 安全认证联想度' },
      { id: 32, role: '联想/认同', note: 'ID 民族文化+华人情感' },
    ],
    gap: '"耐久"在 KPI 里闪现 1 次，没沉淀为系统性品牌资产' },

  flywheel: { name: '飞轮 (Growth Flywheel)', count: 4,
    items: [
      { id: 2, role: 'BD 飞轮', note: 'KOL→社群→Daraz→口碑→俱乐部' },
      { id: 8, role: 'BD 圈层', note: '达卡吉大港俱乐部→会员→配件' },
      { id: 16, role: 'ID 圈层', note: 'Strava→KOL→会员→配件' },
    ],
    gap: 'V1 飞轮假设新用户来自"被内容吸引"，没考虑"老用户升维"路径' },
};

// V2 草稿（基于 4 框架 + Q1-Q4 答案）
const V2_DRAFT = {
  core_narrative: '凤凰让每一程代步，都走得更久更远。',
  core_logic: '耐久=心智资产（显性）/ 安全认证=产品底线（隐性）。客户买单因为"骑 3 年不坏想升级"，认证是"不偷工减料"的证明而非营销 hook。',
  four_frames: {
    stp: {
      segmentation: '基础代步骑行者（5K-10K BDT）/ 中端过渡骑行者（10K-22K BDT）/ 中高端玩家（22K+ BDT 或 8-18M IDR）',
      targeting: '主目标：基础→中端过渡人群（3 年换车周期内的升维机会）；次目标：中端→中高端玩家（UCI 公路车赛道）',
      positioning: '陪伴升级的耐久品牌 —— 区别于 Polygon（专业竞技）/ Trek（高端进口）/ Dream Cycle（多品牌渠道）',
    },
    '4p': {
      product: '入门=通勤车（5-10K BDT）/ 中端=26-29 寸 MTB（10-22K BDT）/ 高端=27.5/29 寸 UCI 公路车（22K+ BDT 或 8-18M IDR）—— 3 个价位 = 升维路径',
      price: '入门包拉量（BDT 5-10K 走量）/ 中端盈利（BDT 14-22K 利润核心）/ 高端占心智（24K+ UCI 心智锚点）',
      place: '基础用户在 Daraz（流量入口）/ 中端通过 MTB 俱乐部 + KOL（信任建立）/ 高端在 DTC 独立站（独家品牌叙事 + 配件复购）',
      promotion: '入门=日常促销 + Daraz 流量 / 中端=俱乐部赞助 + KOL 实测 / 高端=UCI 赛事赞助 + 探险故事 + 3 年老用户证言',
    },
    brand_assets: {
      identity: '"陪伴升级的耐久品牌"',
      awareness: 'BD=耐久认知占有率；ID=华人情感共鸣 + 百年民族品牌',
      loyalty: '会员体系（3 年换车周期触达）+ 配件复购生态',
      association: '"3 年还骑得动" 用户证言 > "SGS 认证" 营销话术',
      perceived_quality: 'SGS+SNI+RoHS+UCI 是"不偷工减料"的证据，不是 hook',
    },
    flywheel: '入门用户 → 3 年口碑证言 → 俱乐部邀请 → 升维中端 MTB → 升维 UCI 公路 → 老用户带新用户',
  },
  unique_insight: 'V2 把"耐久"从 V1 的 1 条 KPI 升为系统核心；把"认证"从 V1 的 hook 降为"产品底线"；新增"升维路径"作为核心叙事。',
};
