import os
import streamlit.components.v1 as components

_RELEASE = True    

if not _RELEASE:
    _chart_to_display = components.declare_component(
        
        "chart_to_display",

        url="http://localhost:3001",
    )
else:

    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _chart_to_display = components.declare_component("chart_to_display", path=build_dir)

def chart_to_display(
        chartType="pieChart", 
        chartData=None, 
        styles=None, 
        chartLayout=None, 
        scatterPlotCustom={ "customComponent": True, "customTooltip": False }, 
        customNodeSize=None,
        scatterToolTipStyle=None,
        key=None, 
        default=None
        ):
    
    component_value = _chart_to_display(
        chartType=chartType, 
        chartData=chartData, 
        chartLayout=chartLayout, 
        styles=styles, 
        scatterPlotCustom=scatterPlotCustom, 
        customNodeSize=customNodeSize,
        scatterToolTipStyle=scatterToolTipStyle,
        key=key, 
        default=default
        )

    return component_value
