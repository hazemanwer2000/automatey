
import plotly.graph_objects
import pandas as pd

class Plot:
    pass

class GanttChart(Plot):
    '''
    Plot a Gantt-Chart, of task(s) against time.

    Note that,
    - Entries shall specify `task`, `start`, `end`, and `duration`.
    - Tasks shall specify `task`, and `category`.
    '''

    def __init__(self, title:str, xaxis_title:str, resolution:float, entries:pd.DataFrame, tasks:pd.DataFrame):
        super().__init__()

        # ? Merge 'tasks' into 'entries'.
        entries = pd.merge(entries, tasks, on='task')

        # ? Assign a unique color per category.
        categories = tasks['category']
        colorPalette = plotly.colors.qualitative.Plotly
        categoryColorMap = {
            category: colorPalette[i % len(colorPalette)]
            for i, category in enumerate(categories)
        }

        # ? Create (blank) figure.
        fig = plotly.graph_objects.Figure()

        # ? Process each entry.
        for idx, entry in entries.iterrows():
            fig.add_trace(plotly.graph_objects.Bar(
                x=[entry['duration']],
                y=[entry['task']],
                base=[entry['start']],
                orientation='h',
                name=entry['category'],
                customdata=[[entry['start'], entry['end'], entry['duration']]],
                hovertemplate=(
                    "Start: %{customdata[0]}<br>"
                    "End: %{customdata[1]}<br>"
                    "Duration: %{customdata[2]}"
                ),
                marker=dict(color=categoryColorMap[entry['category']]),
                showlegend=False,
                width=0.4
            ))

        # ? Customize figure.
        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            barmode='stack',
            xaxis=dict(dtick=resolution, showgrid=True),
            yaxis=dict(dtick=1, showgrid=True, autorange="reversed"),
        )

        fig.show()