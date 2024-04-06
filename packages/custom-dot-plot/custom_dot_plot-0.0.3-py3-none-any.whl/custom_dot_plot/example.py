import streamlit as st
from __init__ import dot_plot


st.set_page_config(layout="wide")

categoryOneData = [
    {
        "index": 0,
        "label": "Level 1",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": True,
                "upgrade": True,
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": True
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": True
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": True
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": True
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": True
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": True
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": True
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": True
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": True
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
    {
        "index": 1,
        "label": "Level 2",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": True,
                "upgrade": True
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": True
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": True
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": True
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": True
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": True
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": True
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": True
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
    {
        "index": 2,
        "label": "Level 3",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": False
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": False
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": True,
                "upgrade": True
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": True
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": True
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": True
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": True
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": True
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
    {
        "index": 3,
        "label": "Level 4",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": False
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": False
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": False
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": False,
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": True,
                "upgrade": True
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": True
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": True
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": True
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
    {
        "index": 4,
        "label": "Level 5",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": False
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": False
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": False
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": False
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": False
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": False
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": True,
                "upgrade": True
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": True,
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
    {
        "index": 5,
        "label": "Level 6",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": False
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": False
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": False
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": False
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": False
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": False
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": False
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": False
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True,
                "upgrade": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    }
]


categoryTwoData = [
    {
        "index": 0,
        "label": "Level 1",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": False
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": True,
                "upgrade": True
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": True
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": True
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": True
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": True
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": True
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": True
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
    {
        "index": 1,
        "label": "Level 2",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": False
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": False
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": False
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": False
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": False
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": True,
                "upgrade": True
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": True
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": True
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": True
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True,
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
    {
        "index": 2,
        "label": "Level 3",
        "data": [
            {
                "index": 0,
                "hero_lvl": 1,
                "active": False
            },
            {
                "index": 1,
                "hero_lvl": 2,
                "active": False
            },
            {
                "index": 2,
                "hero_lvl": 3,
                "active": False
            },
            {
                "index": 3,
                "hero_lvl": 4,
                "active": False
            },
            {
                "index": 4,
                "hero_lvl": 5,
                "active": False
            },
            {
                "index": 5,
                "hero_lvl": 6,
                "active": False
            },
            {
                "index": 6,
                "hero_lvl": 7,
                "active": False
            },
            {
                "index": 7,
                "hero_lvl": 8,
                "active": False
            },
            {
                "index": 8,
                "hero_lvl": 9,
                "active": False
            },
            {
                "index": 9,
                "hero_lvl": 10,
                "active": False
            },
            {
                "index": 10,
                "hero_lvl": 11,
                "active": False
            },
            {
                "index": 11,
                "hero_lvl": 12,
                "active": True,
                "upgrade": True
            },
            {
                "index": 12,
                "hero_lvl": 13,
                "active": True
            },
            {
                "index": 13,
                "hero_lvl": 14,
                "active": True
            },
            {
                "index": 14,
                "hero_lvl": 15,
                "active": True
            }
        ]
    },
]
Legends = [
    {
      "index": 0, "label": "Player level active", "color": "#000000a8", "border": "white"
    },
    {
      "index": 1, "label": "Player level inactive", "color": "white", "border": "black"
    },
    {
      "index": 2, "label": "Player level upgraded", "color": "white", "border": "black", "inner": "black"
    }

]

columnTitle="Hero Level"
indexTitle="Skill level"
firstCategoryTitle="Skill 1"
secondCategoryTitle="Skill 2"


with st.columns([1,8,1])[1]:
    dot_plot(categoryOneData=categoryOneData, categoryTwoData=categoryTwoData, indexTitle=indexTitle, columnTitle=columnTitle, firstCategoryTitle=firstCategoryTitle, secondCategoryTitle=secondCategoryTitle, Legends=Legends)



