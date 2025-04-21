
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

            def __init__(self, figure:plotly.graph_objects.Figure):
                super().__init__()
                self.figure = figure

            def view(self):
                self.figure.show(config=INTERNAL.Implementation.plotly.config)
            
            def saveAs(self, f:FileUtils.File, isSmallerSize:bool=True, format=Formats.HTML):
                if f.isExists():
                    raise ExceptionUtils.ValidationError("Destination file already exists.")
                include_plotlyjs = 'cdn' if isSmallerSize else 'embed'
                plotly.io.write_html(self.figure, str(f),
                                     full_html=True, include_plotlyjs=include_plotlyjs,
                                     config=INTERNAL.Implementation.plotly.config)

class Tracing:

    class Timeline(INTERNAL.Implementation.plotly):
        '''
        Plot a timeline, of task(s) against time.

        Note that,
        - `entries` shall specify `task`, `start`, `duration`, and optionally, more custom field(s).
        - `tasks` shall specify `task` (unique), `category` (used for coloring), and optionally, more custom field(s).
        - `display_fields` shall specify field(s) to display upon hover.
        '''

        def __init__(self, title:str, xaxis_title:str, resolution:float, entries:pd.DataFrame, tasks:pd.DataFrame, display_fields:list):
            
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
                for idx, display_field in enumerate(display_fields):
                    hovertemplate_item = StringUtils.Normalize.asTitle(display_field) + ": %{customdata[" + f"{idx}" "]}"
                    hovertemplate_list.append(hovertemplate_item)
                hovertemplate = "<br>".join(hovertemplate_list) + "<extra></extra>"

                # ? ? Construct 'customdata'.
                customdata = []
                for display_field in display_fields:
                    customdata.append(entry[display_field])

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

        def addMarkers(self, markers:pd.DataFrame, display_fields:list):
            '''
            Add markers at specific instants, along each task.

            Note that,
            - `markers` shall specify `task`, `time`, and optionally, more custom field(s).
            - `display_fields` shall specify field(s) to display upon hover.
            '''
            # ? Process each entry.
            for idx, marker in markers.iterrows():

                # ? ? Construct 'hovertemplate'.
                hovertemplate_list = []
                for idx, display_field in enumerate(display_fields):
                    hovertemplate_item = StringUtils.Normalize.asTitle(display_field) + ": %{customdata[" + f"{idx}" "]}"
                    hovertemplate_list.append(hovertemplate_item)
                hovertemplate = "<br>".join(hovertemplate_list) + "<extra></extra>"

                # ? ? Construct 'customdata'.
                customdata = []
                for display_field in display_fields:
                    customdata.append(marker[display_field])

                scatter = plotly.graph_objects.Scatter(
                    x=[marker['time']],
                    y=[marker['task']],
                    mode='markers',
                    marker=dict(symbol='square', size=10, color='black'),
                    customdata=[customdata],
                    hovertemplate=hovertemplate,
                    showlegend=False
                )

                self.figure.add_trace(scatter)
