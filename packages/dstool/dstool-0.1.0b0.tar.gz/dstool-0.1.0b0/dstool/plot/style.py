def set_plotly_theme(fig):
    fig.update_layout(plot_bgcolor="white")
    fig.update_xaxes(
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    fig.update_yaxes(
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    return fig


def set_font(fig):
    fig.update_layout(
        font_family="Arial",
        font_color="black",
        title_font_family="Arial",
        title_font_color="black",
        legend_title_font_color="black",
        title=dict(font=dict(size=36)),
        legend=dict(font=dict(size=32)),
        legend_title=dict(font=dict(size=28)),
    )
    fig.update_xaxes(title=dict(font=dict(size=28)), tickfont_size=30)
    fig.update_yaxes(title=dict(font=dict(size=28)), tickfont_size=30)
    return fig
