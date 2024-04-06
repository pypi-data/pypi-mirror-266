import os
import streamlit.components.v1 as components

_RELEASE = False

if not _RELEASE:
    _dot_plot = components.declare_component(
        "dot_plot",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _dot_plot = components.declare_component("dot_plot", path=build_dir)


def dot_plot(categoryOneData=None, categoryTwoData=None, columnTitle=None, indexTitle=None, secondCategoryTitle=None, firstCategoryTitle=None, Legends=None, styles=None, key=None, default=None):
    
    component_value = _dot_plot(categoryOneData=categoryOneData, categoryTwoData=categoryTwoData, columnTitle=columnTitle, indexTitle=indexTitle, secondCategoryTitle=secondCategoryTitle, firstCategoryTitle=firstCategoryTitle, Legends=Legends, styles=styles, key=key, default=default)

    return component_value
