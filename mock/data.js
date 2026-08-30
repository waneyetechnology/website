window.WANEYE_REPORTS = {
  global: {
    edition: "Global edition", date: "August 23, 2026", time: "12:16 UTC", score: 58, sentiment: "Measured confidence", sources: 95,
    themes: ["Fiscal pressure", "AI infrastructure", "Digital assets", "Trade friction", "Consumer strain"],
    highlights: [
      "U.S. debt crosses $40 trillion, putting long yields and mortgage markets under renewed pressure despite Treasury liquidity operations.",
      "Alphabet and Amazon push combined AI capital spending toward $420 billion, extending demand for foundries, networking and power infrastructure.",
      "Bitcoin clears $78,500 as institutional flows and liquidity expectations lift digital assets across the board.",
      "U.S. trade friction with key partners adds fresh pressure to cross-border retail, consumer goods and agriculture supply chains."
    ],
    sectors: [
      {name:"Technology & AI", direction:"Constructive", tone:"up", trend:"Mega-cap infrastructure buildout supports foundries, hardware and specialist networking.", implication:"Demand is visible; valuation now depends on proving monetisation.", metric:"$420B", metricLabel:"AI capex signal"},
      {name:"Fixed Income & Real Estate", direction:"Cautious", tone:"down", trend:"The sovereign debt overhang is keeping long yields and mortgage rates elevated.", implication:"Short duration and cash-equivalent yields remain comparatively attractive.", metric:"4.35%", metricLabel:"Top short yield"},
      {name:"Digital Assets", direction:"Positive", tone:"up", trend:"Macro liquidity and institutional accumulation support broad-based momentum.", implication:"Bitcoin and high-liquidity altcoins remain highly rate-sensitive.", metric:"$78.5K", metricLabel:"BTC reference"},
      {name:"Consumer & Retail", direction:"Selective", tone:"flat", trend:"Household cost pressure is widening the gap between value-led and legacy retailers.", implication:"Pricing power and flexible domestic sourcing matter most.", metric:"Mixed", metricLabel:"Margin outlook"},
      {name:"Energy & Materials", direction:"Constructive", tone:"up", trend:"Shipping constraints and structural power demand support commodity pricing.", implication:"Gold and copper hedge fiscal risk while serving electrification demand.", metric:"↑", metricLabel:"Demand bias"}
    ],
    risks: [
      {name:"Sovereign debt & yield dislocation", impact:"High", likelihood:"High", mitigation:"Prefer short duration and hard-asset hedges.", x:82,y:18},
      {name:"AI capex digestion", impact:"High", likelihood:"Medium", mitigation:"Prioritise profitable picks-and-shovels providers.", x:58,y:24},
      {name:"Shipping vulnerabilities", impact:"Medium", likelihood:"High", mitigation:"Underwrite freight volatility and route exposure.", x:78,y:52},
      {name:"Tariff escalation", impact:"Medium", likelihood:"High", mitigation:"Favour flexible, domestically sourced operators.", x:74,y:63}
    ],
    opportunities: [
      {title:"Own the AI infrastructure layer", horizon:"MEDIUM / LONG", tickers:["TSM","NVDA","AMZN","GOOGL"], rationale:"Multi-year capital commitments improve revenue visibility for mission-critical foundries, power and networking."},
      {title:"Capture short-duration income", horizon:"SHORT / MEDIUM", tickers:["IGSB","SHY","LQD"], rationale:"High-quality short duration offers useful carry without taking excessive rate sensitivity."},
      {title:"Add monetary scarcity hedges", horizon:"MEDIUM", tickers:["GLD","IBIT","ETHE"], rationale:"Fiscal expansion and liquidity interventions support scarce monetary assets."}
    ],
    defensive: [
      {title:"Trim rate-sensitive housing & retail", horizon:"SHORT / MEDIUM", tickers:["ITB","XRT","BYND"], rationale:"Mortgage pressure and household inflation threaten turnover and discretionary margins."},
      {title:"Raise portfolio quality", horizon:"LONG", tickers:["SCHD","VIG","NOBL"], rationale:"Cash-generative dividend growers provide discipline as broad-market income compresses."}
    ],
    short:"Markets are likely to remain range-bound, with volatility shaped by central-bank commentary, sovereign bond supply and AI capex digestion.",
    long:"AI and energy infrastructure can sustain earnings growth, but compressed risk premiums and fiscal pressure demand active, quality-led selection.",
    catalysts:["Federal Reserve policy guidance","U.S. Treasury issuance and liquidity operations","Trade negotiations with Canada and global partners","Mega-cap AI return-on-investment disclosures","Red Sea and Middle East transit security"],
    news:[
      {index:2,title:"India Leaves the Door Ajar for China’s Investors",source:"Yahoo Finance",date:"22 AUG",url:"https://finance.yahoo.com/economy/policy/articles/india-leaves-door-ajar-china-123300050.html"},
      {index:5,title:"US Push to Isolate Iran Runs Into China",source:"Bloomberg",date:"23 AUG",url:"https://www.bloomberg.com/news/videos/2026-08-23/us-push-to-isolate-iran-runs-into-china-video"},
      {index:25,title:"Gold remains strong amid U.S. debt concerns",source:"Yahoo Finance",date:"21 AUG",url:"https://finance.yahoo.com/personal-finance/investing/article/gold-prices-today-friday-august-21-2026-gold-remains-strong-amid-us-debt-concerns-161052751.html"}
    ]
  },
  au: {
    edition:"Australia edition", date:"23 August 2026", time:"21:53 AEST", score:34, sentiment:"Defensive bias", sources:68,
    themes:["Bank credit", "Housing reset", "Energy volatility", "Household pressure", "Gold resilience"],
    highlights:[
      "The ASX records a second weekly decline as a broad bank sell-off exposes concern around credit quality and housing stress.",
      "Record house-price falls deepen the property correction and create a difficult backdrop for financials and listed real estate.",
      "Escalating Middle East tensions lift oil prices and risk premia while domestic energy policy remains uncertain.",
      "An income recession and weaker discretionary demand are increasing pressure across the consumer complex."
    ],
    sectors:[
      {name:"Financials / Banks",direction:"Negative",tone:"down",trend:"Mortgage stress and house-price weakness are pressuring credit expectations.",implication:"Margins, bad-debt provisions and dividend resilience move into focus.",metric:"2 wks",metricLabel:"Sell-off duration"},
      {name:"Materials / Mining",direction:"Mixed",tone:"flat",trend:"Gold optimism contrasts with softer China-linked bulk commodities.",implication:"Gold exposure offers relative strength; iron ore remains constrained.",metric:"Gold",metricLabel:"Relative leader"},
      {name:"Energy",direction:"Positive",tone:"up",trend:"Geopolitical supply risk lifts oil while domestic policy clouds the long view.",implication:"Near-term producers benefit, though local gas policy remains a drag.",metric:"↑ Oil",metricLabel:"Price impulse"},
      {name:"Consumer",direction:"Negative",tone:"down",trend:"An income recession is compressing household spending and operating margins.",implication:"Essentials and resilient balance sheets are preferred.",metric:"↓",metricLabel:"Demand bias"},
      {name:"Property / REITs",direction:"Cautious",tone:"down",trend:"Record house-price falls and higher cap-rate risk weigh on the sector.",implication:"Wait for evidence of housing stabilisation before adding exposure.",metric:"Record",metricLabel:"Price decline"},
      {name:"Technology",direction:"Cautious",tone:"flat",trend:"Global AI valuation warnings raise the hurdle for long-duration growth.",implication:"Prefer cash-generative operators over growth at any price.",metric:"High",metricLabel:"Valuation risk"}
    ],
    risks:[
      {name:"Housing spillover into bank losses",impact:"High",likelihood:"High",mitigation:"Reduce broad financial exposure.",x:84,y:16},
      {name:"Middle East energy escalation",impact:"High",likelihood:"Medium",mitigation:"Use energy and gold as portfolio hedges.",x:58,y:22},
      {name:"Income recession",impact:"High",likelihood:"High",mitigation:"Shift toward staples and quality income.",x:80,y:30},
      {name:"Fiscal tightening",impact:"Medium",likelihood:"High",mitigation:"Watch the RBA response and duration risk.",x:74,y:57},
      {name:"AI valuation correction",impact:"Medium",likelihood:"Medium",mitigation:"Trim speculative technology exposure.",x:52,y:64}
    ],
    opportunities:[
      {title:"Overweight gold and energy",horizon:"SHORT",tickers:["GOLD.AX","WPM.AX","WDS.AX"],rationale:"Geopolitical and inflation risk support commodity hedges."},
      {title:"Select defensive consumer income",horizon:"MEDIUM",tickers:["WES.AX","WOW.AX"],rationale:"Essential demand and dividends offer resilience through income pressure."}
    ],
    defensive:[
      {title:"Reduce concentrated bank exposure",horizon:"SHORT",tickers:["CBA.AX","ANZ.AX","NAB.AX"],rationale:"Housing weakness threatens asset quality and earnings visibility."},
      {title:"Hedge AUD and broad beta",horizon:"SHORT",tickers:["AUDUSD","^AXJO"],rationale:"Trade and geopolitical uncertainty raise downside volatility."},
      {title:"Wait on listed property",horizon:"MEDIUM",tickers:["^AXRP","GPW.AX"],rationale:"Cap rates may widen before housing conditions stabilise."}
    ],
    short:"ASX weakness may persist over one to three months as bank credit, housing data and oil volatility dominate the tape.",
    long:"The outlook remains cautious, though gold, energy and eventual housing stabilisation could support recovery as the cycle develops.",
    catalysts:["RBA cash-rate decision","Monthly housing price data","Middle East de-escalation or escalation","Iron ore and LNG trajectory","ASX bank credit-cost guidance"],
    news:[
      {index:27,title:"Delayed at Sydney Airport? Pilots say don’t just blame air traffic control",source:"Sydney Morning Herald",date:"23 AUG",url:"https://www.smh.com.au/business/companies/delayed-at-sydney-airport-pilots-say-air-traffic-control-isn-t-the-only-thing-to-blame-20260818-p60pd1.html"},
      {index:32,title:"Fourth Sydney Airport safety incident under investigation",source:"Sydney Morning Herald",date:"21 AUG",url:"https://www.smh.com.au/business/companies/fourth-sydney-airport-safety-incident-under-investigation-in-as-many-weeks-20260821-p60qca.html"},
      {index:47,title:"Medtronic vs. Tenet Healthcare: which offers better long-term growth?",source:"Yahoo Finance",date:"23 AUG",url:"https://finance.yahoo.com/healthcare/articles/medtronic-vs-tenet-healthcare-healthcare-194303713.html"}
    ]
  },
  cn: {
    edition:"大中华区版", date:"2026年08月23日", time:"20:20 CST", score:68, sentiment:"偏积极", sources:150,
    themes:["人工智能基础设施", "人形机器人", "贵金属", "业绩分化", "监管规范"],
    highlights:[
      "AI基础设施需求持续转化为业绩，光模块、芯片及专业上游供应商加速扩产。",
      "人形机器人在技术指标取得新突破后吸引大量资本关注，商业化落地仍是核心验证点。",
      "黄金与工业金属价格走强，大型资源企业的盈利预期进一步改善。",
      "政策支持与财政收入改善同步推进，信息披露及退市监管亦持续收紧。"
    ],
    sectors:[
      {name:"半导体与人工智能",direction:"积极",tone:"up",trend:"订单及业绩共同验证算力基础设施需求正在加速。",implication:"产业周期正由预期驱动转向基本面兑现。",metric:"↑",metricLabel:"资本开支周期"},
      {name:"人形机器人",direction:"新兴",tone:"up",trend:"技术突破与投资热度使具身智能持续处于市场焦点。",implication:"商业场景与零部件量产能力将决定最终领先者。",metric:"早期",metricLabel:"应用阶段"},
      {name:"有色金属与黄金",direction:"积极",tone:"up",trend:"金价创出新高，铜价保持强势，为资源企业盈利提供支撑。",implication:"大型资源企业具备较高的盈利可见度。",metric:"$4,600",metricLabel:"黄金参考价"},
      {name:"新能源材料",direction:"精选",tone:"flat",trend:"固态电池中试持续推进，传统产业链竞争依然激烈。",implication:"重点关注已验证的新一代材料及具备全球成本优势的企业。",metric:"中试",metricLabel:"商业化阶段"},
      {name:"银行与资产管理",direction:"稳定",tone:"flat",trend:"优质区域银行经营改善，行业信息披露规则进一步收紧。",implication:"高股息金融资产仍是机构底仓的重要组成部分。",metric:"股息率",metricLabel:"主要因子"}
    ],
    risks:[
      {name:"贸易及关税摩擦升级",impact:"高",likelihood:"高",mitigation:"优先配置内需方向及出口市场多元化企业。",x:82,y:18},
      {name:"财务报告与信披风险",impact:"中",likelihood:"中",mitigation:"规避信披质量较弱或存在调查风险的公司。",x:54,y:58},
      {name:"商品价格及杠杆波动",impact:"中",likelihood:"中",mitigation:"控制衍生品风险敞口与单一持仓规模。",x:60,y:66}
    ],
    opportunities:[
      {title:"布局AI核心供应链龙头",horizon:"中长期",tickers:["300308.SZ","688256.SH","9988.HK"],rationale:"资本开支与业绩动能提升算力产业链的盈利可见度。"},
      {title:"超配大型黄金与铜矿企业",horizon:"中长期",tickers:["601899.SH","2899.HK","600547.SH"],rationale:"商品价格高位与产量增长共同强化盈利质量。"},
      {title:"精选下一代电池材料",horizon:"短中期",tickers:["002709.SZ","301211.SZ"],rationale:"中试投产为部分企业带来商业化拐点机会。"}
    ],
    defensive:[
      {title:"保留优质高股息底仓",horizon:"长期",tickers:["600028.SH","601009.SH","510300.SH"],rationale:"稳定现金流与合理估值可对冲外部市场波动。"},
      {title:"退出缺乏业绩支撑的概念交易",horizon:"短期",tickers:["301117.SZ","588000.SH"],rationale:"信披及退市监管趋严将持续压制基本面薄弱标的。"}
    ],
    short:"科技成长与资源板块推动结构性轮动，业绩披露期促使资金进一步向基本面扎实的龙头集中。",
    long:"国内政策支持、人工智能投资及潜在的全球宽松周期，有望共同推动盈利修复与估值重塑。",
    catalysts:["国产AI芯片商业化进展","支持民营企业账款支付的政策落地","美联储政策转向节点","固态电池量产里程碑","人形机器人订单转化"],
    news:[
      {index:2,title:"中钨高新，上半年净利增超280%！股价曾暴涨逾12倍",source:"证券时报",date:"8月23日",url:"https://www.stcn.com/article/detail/4102865.html"},
      {index:20,title:"27家百亿私募重仓股揭晓！新进29只个股，减持7只",source:"证券时报",date:"8月23日",url:"https://www.stcn.com/article/detail/4102672.html"},
      {index:23,title:"周一亚太早盘 WTI原油期货价格跌0.68%",source:"东方财富",date:"8月24日",url:"https://finance.eastmoney.com/a/202608243850452768.html"}
    ]
  }
};
