def animation_refresh(cyclist:Human2D)->None:
    run_anim = st.toggle("Start pedalling", value=True)
    if 't' not in st.session_state:
        st.session_state.t = 0

    placeholder=st.empty()
    x, y,_,_ = cyclist.animation_step_plotly(0)
    time_step=0.1
    while True:
        if run_anim:
            st.session_state.t += time_step
            t = st.session_state.t*2*np.pi*time_step
            x, y,_,_ = cyclist.animation_step_plotly(t)

        fig = go.Figure(
            go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color="#1404F7", width=5))
            ,layout=go.Layout(
                plot_bgcolor="#FBFAFA"
                )
            )
        fig.update_layout(
            xaxis=dict(range=[-800, 400],showgrid=False),
            yaxis=dict(range=[-1000, 400],showgrid=False,scaleanchor="x",scaleratio=1),
            height=800)
        
        # Wyświetlamy
        placeholder.plotly_chart(fig, width='content', key="Pedalling stick figure",config={'displayModeBar': False})
        time.sleep(0.01)