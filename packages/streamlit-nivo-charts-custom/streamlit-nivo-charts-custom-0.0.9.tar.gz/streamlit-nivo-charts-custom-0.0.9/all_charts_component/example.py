import streamlit as st
# from __init__ import chart_to_display
from all_charts_component import chart_to_display

st.set_page_config(layout="wide")

chartData = [
  {
    "damageType": "Final Skill Damage",
    "Physical": 84,
    "Magical": 86,
  },
  {
    "damageType": "Total non-elemental",
    "Base": 129,
    "Extra": 178,
    "Sustained": 196,
  },
  {
    "damageType": "Active Passive",
    "Active": 101,
    "Passive": 65,
  },
  {
    "damageType": "Frequency of hits",
    "Multi-hits": 70,
    "Single hit": 152
  }
]

chartLayout = {
    "keys":[
            'Physical',
            'Magical',
            'Base',
            'Extra',
            'Sustained',
            'Active',
            'Passive',
            'Multi-hits',
            'Single hit'
        ],
    "indexBy":"damageType"
}

chart_to_display(chartData=chartData, chartType="barchart", chartLayout=chartLayout)


pie_chart_ = [
  {
    "Hero": "Claude",
    "Percentage of total": 1.41,
    "label": "Claude"
  },
  {
    "Hero": "Clint",
    "Percentage of total": 4.85,
    "label": "Clint"
  },
  {
    "Hero": "Edith",
    "Percentage of total": 30.54,
    "label": "Edith"
  },
  {
    "Hero": "Hanabi",
    "Percentage of total": 3.4,
    "label": "Hanabi"
  },
  {
    "Hero": "Irithel",
    "Percentage of total": 4.6,
    "label": "Irithel"
  },
  {
    "Hero": "Karrie",
    "Percentage of total": 7.26,
    "label": "Karrie"
  },
  {
    "Hero": "Kimmy",
    "Percentage of total": 10.35,
    "label": "Kimmy"
  },
  {
    "Hero": "Layla",
    "Percentage of total": 12.64,
    "label": "Layla"
  },
  {
    "Hero": "Melissa",
    "Percentage of total": 10.03,
    "label": "Melissa"
  },
  {
    "Hero": "Miya",
    "Percentage of total": 14.92,
    "label": "Miya"
  }
]

pie_chart_layout_ = {
        "id":"Hero",
        "value":"Percentage of total",
        "margin":{ "top": 40, "right": 80, "bottom": 50, "left": 80 },
        "enableArcLabels":False,
        "innerRadius":0.5,
        "padAngle":0.7,
        "cornerRadius":3,
        "activeOuterRadiusOffset":8,
        "borderWidth":1,
        "colors":{ "scheme": 'greys' },
        "borderColor":{
                "from": 'color',
                "modifiers": [
                    [
                        'darker',
                        0.2
                    ]
                ]
            },
        "arcLinkLabelsSkipAngle":10,
        "arcLinkLabelsTextColor":"#333333",
        "arcLinkLabelsThickness":2,
        "arcLinkLabelsColor":{ "from": 'color' },
        "arcLabelsSkipAngle":10,
        "legends":[]
    }

chart_to_display(chartData=pie_chart_, chartType="pieChart", chartLayout=pie_chart_layout_)

data_ = [{
            'id': 'Total Skill Damage Sum',
            'data': [
                {'x': 0,
                  'hero': 'Bruno',
                  'y': 4028.983785981628,
                  'Img': 'http://localhost:8501/app/static/heroes/Bruno.png'},
                {'x': 1,
                  'hero': 'Claude',
                  'y': 3044.7647153292955,
                  'Img': 'http://localhost:8501/app/static/heroes/Claude.png'},
                {'x': 2,
                  'hero': 'Clint',
                  'y': 1266.4786745074477,
                  'Img': 'http://localhost:8501/app/static/heroes/Clint.png'},
                {'x': 3,
                  'hero': 'Edith',
                  'y': 1014.2804345938944,
                  'Img': 'http://localhost:8501/app/static/heroes/Edith.png'},
                {'x': 4,
                  'hero': 'Granger',
                  'y': 4754.352070501903,
                  'Img': 'http://localhost:8501/app/static/heroes/Granger.png'},
                {'x': 5,
                  'hero': 'Hanabi',
                  'y': 1518.792057618723,
                  'Img': 'http://localhost:8501/app/static/heroes/Hanabi.png'},
                {'x': 6,
                  'hero': 'Irithel',
                  'y': 3322.4989238308485,
                  'Img': 'http://localhost:8501/app/static/heroes/Irithel.png'},
                {'x': 7,
                  'hero': 'Karrie',
                  'y': 4345.433910143908,
                  'Img': 'http://localhost:8501/app/static/heroes/Karrie.png'},
                {'x': 8,
                  'hero': 'Kimmy',
                  'y': 3258.6523651328207,
                  'Img': 'http://localhost:8501/app/static/heroes/Kimmy.png'},
                {'x': 9,
                  'hero': 'Layla',
                  'y': 9800.203011290123,
                  'Img': 'http://localhost:8501/app/static/heroes/Layla.png'},
                {'x': 10,
                  'hero': 'Lesley',
                  'y': 1847.759260757279,
                  'Img': 'http://localhost:8501/app/static/heroes/Lesley.png'},
                {'x': 11,
                  'hero': 'Melissa',
                  'y': 3432.9756480348074,
                  'Img': 'http://localhost:8501/app/static/heroes/Melissa.png'}
              ]
        }]


scatter_plot_layout = {
    "margin":{ "top": 30, "right": 30, "bottom": 70, "left": 90 },
    "xScale":{ "type": 'linear', "min": 0, "max": 'auto' },
    "xFormat":">-.2f",
    "yScale":{ "type": 'linear', "min": 0, "max": 'auto'},
    "yFormat":">-.2f",
    "enableGridY":False,
    "enableGridX":False,
    "colors":{ "scheme": 'brown_blueGreen' },
    # "layers":["annotations"],
    # "annotations":[
    #     {
    #         "type": 'circle',
    #         "match": { "x": 10 },
    #         "noteX": 1,
    #         "noteY": 1,
    #         "offset": 3,
    #         "noteTextOffset": -3,
    #         "noteWidth": 1,
    #         "note": 'an annotation',
    #     },
    # ],
      "markers":[
          {
            "axis": "y",
            "value": 2000,
            "legend": "Mean",
            "lineStyle": {
              "stroke": "charcoal",
            },
            "textStyle": {
              "fill": "charcoal",
            },
          },
        ]

} 

chart_to_display(chartType="scatterPlot", chartData=data_, chartLayout=scatter_plot_layout)

data_ = [
  {
    "id": "java",
    # "hero": "java",
    "value": 214,
    "color": "hsl(330, 70%, 50%)"
  },
  {
    "id": "javascript",
    # "hero": "javascript",
    "value": 395,
    "color": "hsl(207, 70%, 50%)"
  },
  {
    "id": "make",
    # "hero": "make",
    "value": 147,
    "color": "hsl(332, 70%, 50%)"
  },
  {
    "id": "css",
    # "hero": "css",
    "value": 291,
    "color": "hsl(136, 70%, 50%)"
  },
  {
    "id": "php",
    # "hero": "php",
    "value": 558,
    "color": "hsl(147, 70%, 50%)"
  }
]

chartLayout = {
    "margin":{ "top": 40, "right": 80, "bottom": 80, "left": 80 },
    "innerRadius":0.5,
    "padAngle":0.7,
    "cornerRadius":3,
    "activeOuterRadiusOffset":8,
    "borderWidth":1,
    "borderColor":{
            "from": 'color',
            "modifiers": [
                [
                    'darker',
                    0.2
                ]
            ]
        },
    "arcLinkLabelsSkipAngle":10,
    "arcLinkLabelsTextColor":"#333333",
    "arcLinkLabelsThickness":2,
    "arcLinkLabelsColor":{ "from": 'color' },
    "arcLabelsSkipAngle":10,
    "legends":[
            {
                "anchor": 'bottom',
                "direction": 'row',
                "justify": False,
                "translateX": 0,
                "translateY": 56,
                "itemsSpacing": 0,
                "itemWidth": 100,
                "itemHeight": 18,
                "itemTextColor": '#999',
                "itemDirection": 'left-to-right',
                "itemOpacity": 1,
                "symbolSize": 18,
                "symbolShape": 'circle',
                "effects": [
                    {
                        "on": 'hover',
                        "style": {
                            "itemTextColor": '#000'
                        }
                    }
                ]
            }
        ]
}

with st.columns([1,10,1])[1]:
    chart_to_display(chartData=data_, chartLayout=chartLayout)

funnel_chart_ = [
  {
    "id": "step_sent",
    "value": 70624,
    "hero": "Sent"
  },
  {
    "id": "step_viewed",
    "value": 51512,
    "hero": "Viewed"
  },
  {
    "id": "step_clicked",
    "value": 48753,
    "hero": "Clicked"
  },
  {
    "id": "step_add_to_card",
    "value": 30771,
    "hero": "Add To Card"
  },
  {
    "id": "step_purchased",
    "value": 24226,
    "hero": "Purchased"
  }
]
funnel_layout_c = {
    "margin":{ "top": 20, "right": 20, "bottom": 20, "left": 20 },
        "valueFormat":">-.4s",
        "enableLabel":True,
        "isInteractive":True,
        "colors":{ "scheme": 'spectral' },
        "borderWidth":20,
        "labelColor":{
            "from": 'color',
            "modifiers": [
                [
                    'darker',
                    3
                ]
            ]
        },
        "beforeSeparatorLength":100,
        "beforeSeparatorOffset":20,
        "afterSeparatorLength":100,
        "afterSeparatorOffset":20,
        "currentPartSizeExtension":10,
        "currentBorderWidth":40,
        "motionConfig":"wobbly"
}

with st.columns([1,10,1])[1]:
    chart_to_display(chartType="funnelChart", chartData=funnel_chart_, chartLayout=funnel_layout_c)

circle_chart = {
  "name": "nivo",
  "color": "hsl(127, 70%, 50%)",
  "children": [ 
      {
        "name": "viz",
        "value":500
      },
      {
        "name": "Dannie",
        "value":100
      }
  ]
}

circle_Chart_layout = {
    "margin":{ "top": 20, "right": 20, "bottom": 20, "left": 20 },
    "id":"name",
    "value":"value",
    "colors":{ "scheme": 'nivo' },
    "childColor":{
        "from": 'color',
        "modifiers": [
            [
                'brighter',
                0.4
            ]
        ]
    },
    "padding":4,
    "enableLabels":True,
    # "labelsFilter": "n=>2===n.node.depth",
    "labelsSkipRadius":10,
    "labelTextColor":{
        "from": 'color',
        "modifiers": [
            [
                'darker',
                2
            ]
        ]
    },
    "borderWidth":1,
    "borderColor":{
        "from": 'color',
        "modifiers": [
            [
                'darker',
                0.5
            ]
        ]
    }
}

with st.columns([1,10,1])[1]:
    chart_to_display(chartType="circlePacking", chartData=circle_chart, chartLayout=circle_Chart_layout)


data_ = [{'id': 'Total Heroes Released Per Year',
  'data': [{'x': 2016, 'y': 27},
   {'x': 2017, 'y': 25},
   {'x': 2018, 'y': 23},
   {'x': 2019, 'y': 15},
   {'x': 2020, 'y': 11},
   {'x': 2021, 'y': 11},
   {'x': 2022, 'y': 6},
   {'x': 2023, 'y': 5},
   {'x': 2024, 'y': 1}]}]


chart_to_display(chartType="lineChart", chartData=data_) #, chartLayout=circle_Chart_layout)
