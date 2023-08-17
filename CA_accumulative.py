import warnings

import pandas as pd
import numpy as np
import plotly.graph_objects as go

ca = pd.read_excel("imf-ca.xls", index_col=0).T
# %%
ca_filtered = ca.applymap(lambda _: np.nan if _ == 'no data' else _)
ca_filtered.astype(float)
# %%
ca_accumulated = ca_filtered.cumsum(skipna=True)
# %%
ca_accumulated_filtered = ca_filtered.copy()
country_code_map = pd.read_csv('wikipedia-iso-country-codes.csv', index_col=0)
available_countries = country_code_map.index
code_map = {}

for name in ca_accumulated.columns:  # type: str
    if name in available_countries:
        country_code = country_code_map.loc[name]['Alpha-3 code']
    elif (short_name := name.split(',')[0]) in available_countries:
        country_code = country_code_map.loc[short_name]['Alpha-3 code']
    else:
        is_found = False

        for _ in available_countries:
            if name in _:
                country_code = _
                warnings.warn(f'{name} not found! Assume to be {_}')
                is_found = True
                break
            elif _ in name:
                country_code = _
                warnings.warn(f'{name} not found! Assume to be {_}')
                is_found = True
                break

        if not is_found:
            ca_accumulated_filtered.drop(columns=name, inplace=True)
            warnings.warn(f'{name} not found dropped!')
            continue

    code_map[name] = country_code
# %%

fig = go.Figure()

# Add traces, one for each slider step
for year in np.arange(1980, 2023):
    ca_acc: pd.Series = ca_accumulated_filtered.loc[year]

    fig.add_trace(
        go.Choropleth(
            locations=[code_map[_] for _ in ca_acc.index],
            z=ca_acc.values,
            text=ca_acc.index,
            # colorscale='Rainbow',
            autocolorscale=False,
            reversescale=True,
            # marker_line_color='darkgray',
            zauto=False,
            zmax=500,
            zmin=-500,
            zmid=0,
            marker_line_width=0.5,
            colorbar_tickprefix='$',
            colorbar_title='Accumulated CA<br>Billions US$',
        )
    )

# Make 10th trace visible
fig.data[-1].visible = True

# Create and add slider
steps = []
for i in range(len(fig.data)):
    step = dict(
        method="update",
        label=f"{1980 + i}",
        args=[{"visible": [False] * len(fig.data)}, {"title": f"{1980 + i}"}],
        # layout attribute
    )
    step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
    steps.append(step)

sliders = [dict(
    active=len(fig.data),
    currentvalue={"prefix": "Year: "},
    pad={"t": 50},
    steps=steps
)]

fig.update_layout(
    title_text='Current Account Accumulated in B$',
    sliders=sliders,
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ),
    annotations=[dict(
        x=0.55,
        y=0.1,
        xref='paper',
        yref='paper',
        showarrow=False
    )]
)

fig.show()
fig.write_html('ca_map.html')
# %%
