import plotly.graph_objects as go


def _emptyScattermap():
    fig = go.Figure(go.Scattermapbox())
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 20, "t": 20, "l": 20, "b": 20},
        annotations=[
            {
                "text": "No Points Found",
                "x": 0.5,
                "y": 0.5,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 18},
            }
        ],
    )
    return fig
