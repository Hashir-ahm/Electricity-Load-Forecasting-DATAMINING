from flask import Flask, render_template, request
from forecast import get_forecast
from cluster import get_clusters
import plotly.graph_objs as go
import plotly.offline as pyo
import os
import uuid

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    forecast_result = None
    cluster_result = None
    forecast_plot_path = None
    cluster_plot_path = None

    if request.method == "POST":
        city = request.form["city"]
        start = request.form["start"]
        end = request.form["end"]
        k = int(request.form.get("k", 3))
        models = request.form.getlist("models")

        # Get forecast and cluster results
        forecast_result = get_forecast(city, f"{start} 00:00:00", f"{end} 23:59:59", models)
        cluster_result = get_clusters(city, f"{start} 00:00:00", f"{end} 23:59:59", k)

        # Create plots directory if not exists
        os.makedirs("static/plots", exist_ok=True)

        # 1. FORECAST PLOT (Interactive)
        if forecast_result and forecast_result['dates']:
            traces = []
            
            # Actual demand trace
            traces.append(go.Scatter(
                x=forecast_result['dates'],
                y=forecast_result['actual'],
                mode='lines',
                name='Actual',
                line=dict(color='black', width=2),
                hoverinfo="x+y+name"
            ))

            # Model prediction traces
            for model, preds in forecast_result['predictions'].items():
                traces.append(go.Scatter(
                    x=forecast_result['dates'],
                    y=preds,
                    mode='lines',
                    name=model,
                    hoverinfo="x+y+name"
                ))

            forecast_layout = go.Layout(
                title=f"Electricity Demand Forecast for {city}",
                xaxis=dict(title='Date', tickangle=45),
                yaxis=dict(title='Demand (MWh)'),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )

            forecast_fig = go.Figure(data=traces, layout=forecast_layout)
            
            # Save as HTML
            forecast_filename = f"forecast_{uuid.uuid4().hex}.html"
            forecast_plot_path = f"plots/{forecast_filename}"
            pyo.plot(forecast_fig, filename=os.path.join("static", forecast_plot_path), auto_open=False)

        # 2. CLUSTER PLOT (Interactive)
        if cluster_result:
            traces = []
            clusters = sorted(set(p["cluster"] for p in cluster_result))
            
            for c in clusters:
                cluster_points = [p for p in cluster_result if p["cluster"] == c]
                traces.append(go.Scatter(
                    x=[p["x"] for p in cluster_points],
                    y=[p["y"] for p in cluster_points],
                    mode='markers',
                    name=f'Cluster {c}',
                    marker=dict(size=10, opacity=0.7),
                    hovertext=[f"Cluster: {c}<br>X: {p['x']:.2f}<br>Y: {p['y']:.2f}" for p in cluster_points],
                    hoverinfo="text"
                ))

            cluster_layout = go.Layout(
                title=f"Demand Pattern Clusters (k={k})",
                xaxis=dict(title='Principal Component 1'),
                yaxis=dict(title='Principal Component 2'),
                hovermode='closest',
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )

            cluster_fig = go.Figure(data=traces, layout=cluster_layout)
            
            # Save as HTML
            cluster_filename = f"cluster_{uuid.uuid4().hex}.html"
            cluster_plot_path = f"plots/{cluster_filename}"
            pyo.plot(cluster_fig, filename=os.path.join("static", cluster_plot_path), auto_open=False)

    return render_template("index.html",
                         forecast_result=forecast_result,
                         cluster_result=cluster_result,
                         forecast_plot=forecast_plot_path,
                         cluster_plot=cluster_plot_path)

if __name__ == "__main__":
    app.run(debug=True) 