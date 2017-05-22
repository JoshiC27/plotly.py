from __future__ import absolute_import

from plotly import colors, exceptions, optional_imports
from plotly.figure_factory import utils
from plotly.graph_objs import graph_objs
from plotly.tools import make_subplots

from numbers import Number
import math

pd = optional_imports.get_module('pandas')

DEFUALT_MARKER_COLOR = '#000000'
TICK_COLOR = '#969696'
AXIS_TITLE_COLOR = '#0f0f0f'
GRID_COLOR = '#ffffff'
LEGEND_COLOR = '#efefef'
PLOT_BGCOLOR = '#e0e0e0'
ANNOT_RECT_COLOR = '#d0d0d0'
HORIZONTAL_SPACING = 0.02
VERTICAL_SPACING = 0.02
LEGEND_BORDER_WIDTH = 1
LEGEND_ANNOT_X = 1.05
LEGEND_ANNOT_Y = 0.5


def _return_label(original_label, facet_labels, facet_var):
    if isinstance(facet_labels, dict):
        label = facet_labels[original_label]
    elif isinstance(facet_labels, str):
        label = '{}: {}'.format(facet_var, original_label)
    else:
        label = original_label
    return label


def _legend_annotation(color_name):
    legend_title = dict(
        textangle=0,
        xanchor='left',
        yanchor='middle',
        x=LEGEND_ANNOT_X,
        y=1.03,
        showarrow=False,
        xref='paper',
        yref='paper',
        text='factor({})'.format(color_name),
        font=dict(
            size=13,
            color='#000000'
        )
    )
    return legend_title


def _annotation_dict(text, lane, num_of_lanes, row_col='col'):
    if row_col == 'col':
        l = 0.05
        w = (1 - (num_of_lanes - 1) * l) / num_of_lanes
        x = ((2 * lane - 1) * w + (2 * lane - 2) * l) / 2.
        y = 1.03
        textangle = 0
    elif row_col == 'row':
        l = 0.03
        w = (1 - (num_of_lanes - 1) * l) / num_of_lanes
        x = 1.03
        y = ((2 * lane - 1) * w + (2 * lane - 2) * l) / 2.
        textangle = 90

    annotation_dict = dict(
        textangle=textangle,
        xanchor='center',
        yanchor='middle',
        x=x,
        y=y,
        showarrow=False,
        xref='paper',
        yref='paper',
        text=text,
        font=dict(
            size=13,
            color=AXIS_TITLE_COLOR
        )
    )
    return annotation_dict

def _axis_title_annotation(text, x_or_y_axis):
    if x_or_y_axis == 'x':
        x_pos = 0.5
        y_pos = -0.1
        textangle = 0
    elif x_or_y_axis == 'y':
        x_pos = -0.1
        y_pos = 0.5
        textangle = 270

    annot = {'font': {'color': '#000000', 'size': 16},
             'showarrow': False,
             'text': text,
             'textangle': textangle,
             'x': x_pos,
             'xanchor': 'center',
             'xref': 'paper',
             'y': y_pos,
             'yanchor': 'middle',
             'yref': 'paper'}
    return annot


def _add_shapes_to_fig(fig, annot_rect_color):
    fig['layout']['shapes'] = []
    for key in fig['layout'].keys():
        if 'xaxis' in key or 'yaxis' in key:
            if fig['layout'][key]['domain'] != [0.0, 1.0]:
                if 'xaxis' in key:
                    fig['layout']['shapes'].append(
                        {'fillcolor': annot_rect_color,
                       'layer': 'below',
                       'line': {'color': annot_rect_color, 'width': 1},
                       'type': 'rect',
                       'x0': fig['layout'][key]['domain'][0],
                       'x1': fig['layout'][key]['domain'][1],
                       'xref': 'paper',
                       'y0': 1.005,
                       'y1': 1.05,
                       'yref': 'paper'}
                    )
                elif 'yaxis' in key:
                    fig['layout']['shapes'].append(
                        {'fillcolor': annot_rect_color,
                         'layer': 'below',
                         'line': {'color': annot_rect_color, 'width': 1},
                         'type': 'rect',
                         'x0': 1.005,
                         'x1': 1.05,
                         'xref': 'paper',
                         'y0': fig['layout'][key]['domain'][0],
                         'y1': fig['layout'][key]['domain'][1],
                         'yref': 'paper'}
                    )


def _facet_grid_color_categorical(df, x, y, facet_row, facet_col, color_name,
                                  colormap, title, height, width, num_of_rows,
                                  num_of_cols, facet_row_labels,
                                  facet_col_labels, scattergl, **kwargs):
    fig = make_subplots(rows=num_of_rows, cols=num_of_cols,
                        shared_xaxes=True, shared_yaxes=True,
                        horizontal_spacing=HORIZONTAL_SPACING,
                        vertical_spacing=VERTICAL_SPACING, print_grid=False)

    annotations = []
    if not facet_row and not facet_col:
        color_groups = list(df.groupby(color_name))
        for group in color_groups:
            trace = graph_objs.Scatter(
                x=group[1][x].tolist(),
                y=group[1][y].tolist(),
                mode='markers',
                type='scatter' + scattergl * 'gl',
                name=group[0],
                marker=dict(
                    color=colormap[group[0]]
                ),
                **kwargs
            )
            fig.append_trace(trace, 1, 1)

    elif facet_row and not facet_col:
        groups_by_facet_row = list(df.groupby(facet_row))
        for j, group in enumerate(groups_by_facet_row):
            for color_val in df[color_name].unique():
                data_by_color = group[1][group[1][color_name] == color_val]
                trace = graph_objs.Scatter(
                    x=data_by_color[x].tolist(),
                    y=data_by_color[y].tolist(),
                    mode='markers',
                    type='scatter' + scattergl * 'gl',
                    name=color_val,
                    marker=dict(
                        color=colormap[color_val]
                    ),
                    **kwargs
                )
                fig.append_trace(trace, j + 1, 1)

            label = _return_label(group[0], facet_row_labels, facet_row)

            annotations.append(
                _annotation_dict(label, num_of_rows - j, num_of_rows,
                                 row_col='row')
            )

    elif not facet_row and facet_col:
        groups_by_facet_col = list(df.groupby(facet_col))
        for j, group in enumerate(groups_by_facet_col):
            for color_val in df[color_name].unique():
                data_by_color = group[1][group[1][color_name] == color_val]
                trace = graph_objs.Scatter(
                    x=data_by_color[x].tolist(),
                    y=data_by_color[y].tolist(),
                    mode='markers',
                    type='scatter' + scattergl * 'gl',
                    name=color_val,
                    marker=dict(
                        color=colormap[color_val]
                    ),
                    **kwargs
                )
                fig.append_trace(trace, 1, j + 1)

            label = _return_label(group[0], facet_col_labels, facet_col)

            annotations.append(
                _annotation_dict(label, j + 1, num_of_cols, row_col='col')
            )

    elif facet_row and facet_col:
        groups_by_facets = list(df.groupby([facet_row, facet_col]))
        tuple_to_facet_group = {item[0]: item[1] for
                                item in groups_by_facets}

        row_values = df[facet_row].unique()
        col_values = df[facet_col].unique()
        color_vals = df[color_name].unique()
        for row_count, x_val in enumerate(row_values):
            for col_count, y_val in enumerate(col_values):
                try:
                    group = tuple_to_facet_group[(x_val, y_val)]
                except KeyError:
                    group = pd.DataFrame([[None, None, None]],
                                         columns=[x, y, color_name])

                for color_val in color_vals:
                    if group.values.tolist() != [[None, None, None]]:
                        group_filtered = group[group[color_name] == color_val]

                        trace = graph_objs.Scatter(
                            x=group_filtered[x].tolist(),
                            y=group_filtered[y].tolist(),
                            mode='markers',
                            type='scatter' + scattergl * 'gl',
                            name=color_val,
                            marker=dict(
                                color=colormap[color_val]
                            ),
                            **kwargs
                        )
                    else:
                        trace = graph_objs.Scatter(
                            x=group[x].tolist(),
                            y=group[y].tolist(),
                            mode='markers',
                            type='scatter' + scattergl * 'gl',
                            name=color_val,
                            marker=dict(
                                color=colormap[color_val]
                            ),
                            showlegend=False,
                            **kwargs
                        )
                    fig.append_trace(trace, row_count + 1, col_count + 1)
                if row_count == 0:
                    label = _return_label(col_values[col_count],
                                          facet_col_labels, facet_col)
                    annotations.append(
                        _annotation_dict(label,
                                         col_count + 1,
                                         num_of_cols,
                                         row_col='col')
                        )
            label = _return_label(row_values[row_count],
                                  facet_row_labels, facet_row)
            annotations.append(
                _annotation_dict(label,
                                 num_of_rows - row_count,
                                 num_of_rows,
                                 row_col='row')
                )

    # add annotations
    fig['layout']['annotations'] = annotations

    return fig


def _facet_grid_color_numerical(df, x, y, facet_row, facet_col, color_name,
                                colormap, title, height, width,
                                num_of_rows, num_of_cols, facet_row_labels,
                                facet_col_labels, scattergl, **kwargs):
    fig = make_subplots(rows=num_of_rows, cols=num_of_cols,
                        shared_xaxes=True, shared_yaxes=True,
                        horizontal_spacing=HORIZONTAL_SPACING,
                        vertical_spacing=VERTICAL_SPACING, print_grid=False)

    annotations = []
    if not facet_row and not facet_col:
        trace = graph_objs.Scatter(
            x=df[x].tolist(),
            y=df[y].tolist(),
            mode='markers',
            type='scatter' + scattergl * 'gl',
            marker=dict(
                color=df[color_name],
                colorscale=colormap,
                showscale=True
            ),
            **kwargs
        )
        fig.append_trace(trace, 1, 1)

    elif facet_row and not facet_col:
        groups_by_facet_row = list(df.groupby(facet_row))
        for j, group in enumerate(groups_by_facet_row):
            trace = graph_objs.Scatter(
                x=group[1][x].tolist(),
                y=group[1][y].tolist(),
                mode='markers',
                type='scatter' + scattergl * 'gl',
                marker=dict(
                    color=df[color_name].tolist(),
                    colorscale=colormap,
                    showscale=True,
                    colorbar=dict(x=1.15)
                ),
                **kwargs
            )
            fig.append_trace(trace, j + 1, 1)

            label = _return_label(group[0], facet_row_labels, facet_row)

            annotations.append(
                _annotation_dict(label, num_of_rows - j,
                                 num_of_rows, row_col='row')
            )

    elif not facet_row and facet_col:
        groups_by_facet_col = list(df.groupby(facet_col))
        for j, group in enumerate(groups_by_facet_col):
            trace = graph_objs.Scatter(
                x=group[1][x].tolist(),
                y=group[1][y].tolist(),
                mode='markers',
                type='scatter' + scattergl * 'gl',
                marker=dict(
                    color=df[color_name].tolist(),
                    colorscale=colormap,
                    showscale=True,
                    colorbar=dict(x=1.15)
                ),
                **kwargs
            )
            fig.append_trace(trace, 1, j + 1)

            label = _return_label(group[0], facet_col_labels, facet_col)

            annotations.append(
                _annotation_dict(label, j + 1, num_of_cols, row_col='col')
            )

    elif facet_row and facet_col:
        groups_by_facets = list(df.groupby([facet_row, facet_col]))
        tuple_to_facet_group = {item[0]: item[1] for
                                item in groups_by_facets}

        row_values = df[facet_row].unique()
        col_values = df[facet_col].unique()
        for row_count, x_val in enumerate(row_values):
            for col_count, y_val in enumerate(col_values):
                try:
                    group = tuple_to_facet_group[(x_val, y_val)]
                except KeyError:
                    group = pd.DataFrame([[None, None, None]],
                                         columns=[x, y, color_name])

                if group.values.tolist() != [[None, None, None]]:
                    trace = graph_objs.Scatter(
                        x=group[x].tolist(),
                        y=group[y].tolist(),
                        mode='markers',
                        type='scatter' + scattergl * 'gl',
                        marker=dict(
                            color=df[color_name].tolist(),
                            colorscale=colormap,
                            showscale=(row_count == 0),
                            colorbar=dict(x=1.15)
                        ),
                        **kwargs
                    )
                else:
                    trace = graph_objs.Scatter(
                        x=group[x].tolist(),
                        y=group[y].tolist(),
                        mode='markers',
                        type='scatter' + scattergl * 'gl',
                        showlegend=False,
                        **kwargs
                    )
                fig.append_trace(trace, row_count + 1, col_count + 1)
                if row_count == 0:
                    label = _return_label(col_values[col_count],
                                          facet_col_labels, facet_col)
                    annotations.append(
                        _annotation_dict(label,
                                         col_count + 1,
                                         num_of_cols,
                                         row_col='col')
                        )
            label = _return_label(row_values[row_count],
                                  facet_row_labels, facet_row)
            annotations.append(
                _annotation_dict(row_values[row_count],
                                 num_of_rows - row_count,
                                 num_of_rows,
                                 row_col='row')
                )

    # add annotations
    fig['layout']['annotations'] = annotations

    return fig


def _facet_grid(df, x, y, facet_row, facet_col, title, height, width,
                num_of_rows, num_of_cols, facet_row_labels, facet_col_labels,
                scattergl, **kwargs):
    fig = make_subplots(rows=num_of_rows, cols=num_of_cols,
                        shared_xaxes=True, shared_yaxes=True,
                        horizontal_spacing=HORIZONTAL_SPACING,
                        vertical_spacing=VERTICAL_SPACING, print_grid=False)
    annotations = []
    if not facet_row and not facet_col:
        trace = graph_objs.Scatter(
            x=df[x].tolist(),
            y=df[y].tolist(),
            mode='markers',
            type='scatter' + scattergl * 'gl',
            marker=dict(
                color=DEFUALT_MARKER_COLOR
            ),
            **kwargs
        )
        fig.append_trace(trace, 1, 1)

    elif facet_row and not facet_col:
        groups_by_facet_row = list(df.groupby(facet_row))
        for j, group in enumerate(groups_by_facet_row):
            trace = graph_objs.Scatter(
                x=group[1][x].tolist(),
                y=group[1][y].tolist(),
                mode='markers',
                type='scatter' + scattergl * 'gl',
                marker=dict(
                    color=DEFUALT_MARKER_COLOR
                ),
                **kwargs
            )
            fig.append_trace(trace, j + 1, 1)

            # custom labels
            if isinstance(facet_row_labels, dict):
                label = facet_row_labels[group[0]]
            elif isinstance(facet_row_labels, str):
                label = '{}: {}'.format(facet_row, group[0])
            else:
                label = group[0]

            label = _return_label(group[0], facet_row_labels, facet_row)

            annotations.append(
                _annotation_dict(label, num_of_rows - j,
                                 num_of_rows, row_col='row')
            )

    elif not facet_row and facet_col:
        groups_by_facet_col = list(df.groupby(facet_col))
        for j, group in enumerate(groups_by_facet_col):
            trace = graph_objs.Scatter(
                x=group[1][x].tolist(),
                y=group[1][y].tolist(),
                mode='markers',
                type='scatter' + scattergl * 'gl',
                marker=dict(
                    color=DEFUALT_MARKER_COLOR
                ),
                **kwargs
            )
            fig.append_trace(trace, 1, j + 1)

            label = _return_label(group[0], facet_col_labels, facet_col)

            annotations.append(
                _annotation_dict(label, j + 1, num_of_cols, row_col='col')
            )

    elif facet_row and facet_col:
        groups_by_facets = list(df.groupby([facet_row, facet_col]))
        tuple_to_facet_group = {item[0]: item[1] for
                                item in groups_by_facets}

        row_values = df[facet_row].unique()
        col_values = df[facet_col].unique()
        for row_count, x_val in enumerate(row_values):
            for col_count, y_val in enumerate(col_values):
                try:
                    group = tuple_to_facet_group[(x_val, y_val)]
                except KeyError:
                    group = pd.DataFrame([[None, None]], columns=[x, y])
                trace = graph_objs.Scatter(
                    x=group[x].tolist(),
                    y=group[y].tolist(),
                    mode='markers',
                    type='scatter' + scattergl * 'gl',
                    marker=dict(
                        color=DEFUALT_MARKER_COLOR
                    ),
                    **kwargs
                )
                fig.append_trace(trace, row_count + 1, col_count + 1)
                if row_count == 0:
                    label = _return_label(col_values[col_count],
                                          facet_col_labels,
                                          facet_col)
                    annotations.append(
                        _annotation_dict(label,
                                         col_count + 1,
                                         num_of_cols,
                                         row_col='col')
                        )

            label = _return_label(row_values[row_count],
                                  facet_row_labels,
                                  facet_row)
            annotations.append(
                _annotation_dict(label,
                                 num_of_rows - row_count,
                                 num_of_rows,
                                 row_col='row')
                )

    # add annotations
    fig['layout']['annotations'] = annotations

    return fig


def create_facet_grid(df, x, y, facet_row=None, facet_col=None,
                      color_name=None, colormap=None, facet_row_labels=None,
                      facet_col_labels=None, title='facet grid', height=600,
                      width=600, scattergl=False, **kwargs):
    """
    Returns figure for facet grid.

    :param (pd.DataFrame) df: the dataframe of columns for the facet grid.
    :param (str) x: the key of the dataframe to be used as the x axis df.
    :param (str) y: the key of the dataframe to be used as the y axis df.
    :param (str) facet_row: the key for row filter column for the facet grid.
    :param (str) facet_col: the key for the column filter column for the facet
        grid.
    :param (str) color_name: the name of your dataframe column that will
        function as the colormap variable.
    :param (str|list|dict) colormap: the param that determines how the
        color_name column colors the data. If the dataframe contains numeric
        data, then a dictionary of colors will group the data categorically
        while a Plotly Colorscale name or a custom colorscale will treat it
        numerically. To learn more about colors and types of colormap, run
        `help(plotly.colors)`.
    :param (str|dict) facet_row_labels: set to either 'name' or a dictionary
        of all the values in the facetting row mapped to some text to show up
        in the label annotations. If None, labelling works like usual.
    :param (str|dict) facet_col_labels: set to either 'name' or a dictionary
        of all the values in the facetting row mapped to some text to show up
        in the label annotations. If None, labelling works like usual.
    :param (str) title: the title of the facet grid figure.
    :param (int) height: the height of the facet grid figure.
    :param (int) width: the width of the facet grid figure.
    :param (bool) scattergl: enables whether or not scattergl points are
        plotted. Default = False
    :param (dict) kwargs: a dictionary of scatterplot arguments.

    """
    if not pd:
        raise exceptions.ImportError(
            "'pandas' must be imported for this figure_factory."
        )

    if not isinstance(df, pd.DataFrame):
        raise exceptions.PlotlyError(
            "You must input a pandas DataFrame."
        )

    # make sure all columns are of homogenous datatype
    utils.validate_dataframe(df)

    for key in [x, y, facet_row, facet_col, color_name]:
        if key is not None:
            try:
                df[key]
            except KeyError:
                raise exceptions.PlotlyError(
                    "x, y, facet_row, facet_col and color_name must be keys "
                    "in your dataframe."
                )

    # make sure dataframe index starts at 0
    df.index = range(len(df))

    num_of_rows = 1
    num_of_cols = 1

    if facet_row:
        num_of_rows = len(df[facet_row].unique())
        if isinstance(facet_row_labels, dict):
            for key in df[facet_row].unique():
                if key not in facet_row_labels.keys():
                    unique_keys = df[facet_row].unique().tolist()
                    raise exceptions.PlotlyError(
                        "If you are using a dictioanry for custom labels for "
                        "the facet row, make sure each key in that column of "
                        "the dataframe is in 'facet_row_labels'. The keys "
                        "you need are {}".format(unique_keys)
                    )
    if facet_col:
        num_of_cols = len(df[facet_col].unique())
        if isinstance(facet_col_labels, dict):
            for key in df[facet_col].unique():
                if key not in facet_col_labels.keys():
                    unique_keys = df[facet_col].unique().tolist()
                    raise exceptions.PlotlyError(
                        "If you are using a dictioanry for custom labels for "
                        "the facet column, make sure each key in that column "
                        "of the dataframe is in 'facet_col_labels'. The keys "
                        "you need are {}".format(unique_keys)
                    )
    show_legend = False
    if color_name:
        if isinstance(df[color_name][0], str):
            show_legend = True
            if isinstance(colormap, dict):
                utils.validate_colors_dict(colormap, 'rgb')

                for val in df[color_name].unique():
                    if val not in colormap.keys():
                        raise exceptions.PlotlyError(
                            "If using 'colormap' as a dictionary, make sure "
                            "all the values of the colormap column are in "
                            "the keys of your dictionary."
                        )
            else:
                # use default plotly colors for dictionary
                default_colors = utils.DEFAULT_PLOTLY_COLORS
                colormap = {}
                j = 0
                for val in df[color_name].unique():
                    if j >= len(default_colors):
                        j = 0
                    colormap[val] = default_colors[j]
                    j += 1
            fig = _facet_grid_color_categorical(df, x, y, facet_row,
                                                facet_col, color_name,
                                                colormap, title, height,
                                                width, num_of_rows,
                                                num_of_cols, facet_row_labels,
                                                facet_col_labels, scattergl,
                                                **kwargs)

        elif isinstance(df[color_name][0], Number):
            if isinstance(colormap, dict):
                show_legend = True
                utils.validate_colors_dict(colormap, 'rgb')

                for val in df[color_name].unique():
                    if val not in colormap.keys():
                        raise exceptions.PlotlyError(
                            "If using 'colormap' as a dictionary, make sure "
                            "all the values of the colormap column are in "
                            "the keys of your dictionary."
                        )
                fig = _facet_grid_color_categorical(df, x, y, facet_row,
                                                    facet_col, color_name,
                                                    colormap, title, height,
                                                    width, num_of_rows,
                                                    num_of_cols,
                                                    facet_row_labels,
                                                    facet_col_labels,
                                                    scattergl, **kwargs)

            elif isinstance(colormap, list):
                colorscale_list = colormap
                utils.validate_colorscale(colorscale_list)

                fig = _facet_grid_color_numerical(df, x, y, facet_row,
                                                  facet_col, color_name,
                                                  colorscale_list, title,
                                                  height, width, num_of_rows,
                                                  num_of_cols,
                                                  facet_row_labels,
                                                  facet_col_labels,
                                                  scattergl, **kwargs)
            elif isinstance(colormap, str):
                if colormap in colors.PLOTLY_SCALES.keys():
                    colorscale_list = colors.PLOTLY_SCALES[colormap]
                else:
                    raise exceptions.PlotlyError(
                        "If 'colormap' is a string, it must be the name "
                        "of a Plotly Colorscale. The available colorscale "
                        "names are {}".format(colors.PLOTLY_SCALES.keys())
                    )
                fig = _facet_grid_color_numerical(df, x, y, facet_row,
                                                  facet_col, color_name,
                                                  colorscale_list, title,
                                                  height, width, num_of_rows,
                                                  num_of_cols,
                                                  facet_row_labels,
                                                  facet_col_labels,
                                                  scattergl, **kwargs)
            else:
                colorscale_list = colors.PLOTLY_SCALES['Reds']
                fig = _facet_grid_color_numerical(df, x, y, facet_row,
                                                  facet_col, color_name,
                                                  colorscale_list, title,
                                                  height, width, num_of_rows,
                                                  num_of_cols,
                                                  facet_row_labels,
                                                  facet_col_labels,
                                                  scattergl, **kwargs)

    else:
        fig = _facet_grid(df, x, y, facet_row, facet_col, title, height,
                          width, num_of_rows, num_of_cols, facet_row_labels,
                          facet_col_labels, scattergl, **kwargs)

    fig['layout'].update(height=height, width=width, title=title)
    fig['layout'].update(plot_bgcolor=PLOT_BGCOLOR)

    # style the axes
    all_axis_keys = []
    for key in fig['layout']:
        if 'xaxis' in key or 'yaxis' in key:
            all_axis_keys.append(key)
            fig['layout'][key]['tickfont'] = {
                'color': TICK_COLOR, 'size': 10
            }
            fig['layout'][key]['gridcolor'] = GRID_COLOR
            fig['layout'][key]['gridwidth'] = 2
            fig['layout'][key]['zeroline'] = False

    # axis titles
    x_title_annot = _axis_title_annotation(x, 'x')
    y_title_annot = _axis_title_annotation(y, 'y')
    fig['layout']['annotations'].append(x_title_annot)
    fig['layout']['annotations'].append(y_title_annot)

    # legend
    fig['layout']['showlegend'] = show_legend
    fig['layout']['legend']['bgcolor'] = LEGEND_COLOR
    fig['layout']['legend']['borderwidth'] = LEGEND_BORDER_WIDTH
    fig['layout']['legend']['x'] = 1.05
    fig['layout']['legend']['y'] = 1
    fig['layout']['legend']['yanchor'] = 'top'

    if show_legend:
        legend_annot = _legend_annotation(color_name)
        fig['layout']['annotations'].append(legend_annot)
        fig['layout']['margin']['r'] = 150

    # add shaded regions behind axis titles
    _add_shapes_to_fig(fig, ANNOT_RECT_COLOR)

    # fix ranges for subplots in same facet row/col
    axis_labels = {'x': [], 'y': []}

    for key in fig['layout']:
        if 'xaxis' in key:
            axis_labels['x'].append(key)
        elif 'yaxis' in key:
            axis_labels['y'].append(key)

    for x_y in ['x', 'y']:
        if len(axis_labels[x_y]) > 1:
            min_ranges = []
            max_ranges = []
            for trace in fig['data']:
                if len(trace[x_y]) > 0:
                    min_ranges.append(min(trace[x_y]))
                    max_ranges.append(max(trace[x_y]))
            while None in min_ranges:
                min_ranges.remove(None)
            while None in max_ranges:
                max_ranges.remove(None)

            min_range = min(min_ranges)
            max_range = max(max_ranges)

            range_are_numbers = (isinstance(min_range, Number) and
                                 isinstance(max_range, Number))

            # floor and ceiling the range endpoints
            if range_are_numbers:
                min_range = math.floor(min_range) - 1
                max_range = math.ceil(max_range) + 1

            # insert ranges into fig
            for key in fig['layout']:
                if '{}axis'.format(x_y) in key and range_are_numbers:
                    fig['layout'][key]['range'] = [min_range, max_range]

    return fig
