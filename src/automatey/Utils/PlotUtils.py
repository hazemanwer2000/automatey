
import automatey.Utils.StringUtils as StringUtils

import plotly.graph_objects
import pandas as pd

class Plot:
    pass

class GanttChart(Plot):
    '''
    Plot a Gantt-Chart, of task(s) against time.

    Note that,
    - `entries` shall specify `task`, `start`, `duration`, and optionally, more custom field(s).
    - `tasks` shall specify `task`, `category` (used for coloring), and optionally, more custom field(s).
    - `hover_fields` shall specify field(s) to display upon hover.
    '''

    def __init__(self, title:str, xaxis_title:str, resolution:float, entries:pd.DataFrame, tasks:pd.DataFrame, hover_fields:list):
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

            # ? ? Construct 'hovertemplate'.
            hovertemplate_list = []
            for idx, hover_field in enumerate(hover_fields):
                hovertemplate_item = StringUtils.Normalize.asTitle(hover_field) + ": %{customdata[" + f"{idx}" "]}"
                hovertemplate_list.append(hovertemplate_item)
            hovertemplate = "<br>".join(hovertemplate_list) + "<extra></extra>"

            # ? ? Construct 'customdata'.
            customdata = []
            for hover_field in hover_fields:
                customdata.append(entry[hover_field])

            fig.add_trace(plotly.graph_objects.Bar(
                x=[entry['duration']],
                y=[entry['task']],
                base=[entry['start']],
                orientation='h',
                customdata=[customdata],
                hovertemplate=hovertemplate,
                marker=dict(color=categoryColorMap[entry['category']]),
                showlegend=False,
                width=0.6
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