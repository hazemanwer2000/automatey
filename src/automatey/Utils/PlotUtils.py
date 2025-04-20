
import automatey.Utils.StringUtils as StringUtils
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

import plotly.graph_objects
import plotly.io
import pandas as pd

class Plot:
    
    def __init__(self):
        pass

    def view(self):
        pass

class Formats:

    class HTML: pass

class INTERNAL:

    class Implementation:

        class plotly(Plot):

            config = {
                'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
                'displaylogo': False
            }

            def __init__(self, figure):
                super().__init__()
                self.figure = figure

            def view(self):
                self.figure.show(config=INTERNAL.Implementation.plotly.config)
            
            def saveAs(self, f:FileUtils.File, format=Formats.HTML):
                if f.isExists():
                    raise ExceptionUtils.ValidationError("Destination file already exists.")
                plotly.io.write_html(self.figure, str(f),
                                     full_html=True, include_plotlyjs='embed',
                                     config=INTERNAL.Implementation.plotly.config)

class GanttChart(INTERNAL.Implementation.plotly):
    '''
    Plot a Gantt-Chart, of task(s) against time.

    Note that,
    - `entries` shall specify `task`, `start`, `duration`, and optionally, more custom field(s).
    - `tasks` shall specify `task`, `category` (used for coloring), and optionally, more custom field(s).
    - `hover_fields` shall specify field(s) to display upon hover.
    '''

    def __init__(self, title:str, xaxis_title:str, resolution:float, entries:pd.DataFrame, tasks:pd.DataFrame, hover_fields:list):
        
        # ? Create (blank) figure.
        figure = plotly.graph_objects.Figure()
        super().__init__(figure)

        # ? Merge 'tasks' into 'entries'.
        entries = pd.merge(entries, tasks, on='task')

        # ? Assign a unique color per category.
        categories = tasks['category']
        colorPalette = plotly.colors.qualitative.Plotly
        categoryColorMap = {
            category: colorPalette[i % len(colorPalette)]
            for i, category in enumerate(categories)
        }

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

            figure.add_trace(plotly.graph_objects.Bar(
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
        figure.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            barmode='stack',
            xaxis=dict(dtick=resolution, showgrid=True),
            yaxis=dict(dtick=1, showgrid=True,
                       autorange="reversed",
                       categoryorder='array',
                       categoryarray=tasks['task']),
        )