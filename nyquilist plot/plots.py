import plotly.graph_objects as go



def input_plot(t_seg, v_seg, i_seg, f):
    fig = go.Figure()
    # Add the measured data

    # First trace - voltage (left y-axis)
    fig.add_trace(go.Scatter(
        x=t_seg,
        y=v_seg,
        mode='markers',
        name='Voltage',
        yaxis='y1'
    ))

    # Second trace - current (right y-axis)
    fig.add_trace(go.Scatter(
        x=t_seg,
        y=i_seg,
        mode='markers',
        name='Current',
        marker=dict(color='orange'),
        yaxis='y2'
    ))
        # Update layout to add a second y-axis
    fig.update_layout(
        title='Input plot for ' + str(f) + 'Hz',
        xaxis=dict(title='Time'),
        yaxis=dict(
            title='Voltage',
            #titlefont=dict(color='blue'),
            tickfont=dict(color='white')
        ),
        yaxis2=dict(
            title='Current',
            #titlefont=dict(color='orange'),
            tickfont=dict(color='orange'),
            overlaying='y',
            side='right'
        ),
        template='plotly_dark',
        showlegend=True,
        dragmode='zoom'
    )
    # Show the plot
    fig.show()