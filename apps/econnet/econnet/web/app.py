from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go
import json

from econnet.simulation.engine import SimulationEngine
from econnet.simulation.scenarios import ScenarioManager

app = FastAPI(title="EconNet Interactive Dashboard")


class GlobalState:
    def __init__(self):
        self.engine = SimulationEngine(config={"graeber": True, "initial_peace": 1.0, "tribute_rate": 0.05})
        self.current_scenario = "Default ABM"
        self.tick_log = []
        self.reset()

    def reset(self):
        self.tick_log.clear()
        if self.current_scenario == "Default ABM":
            self.engine = SimulationEngine(config={"graeber": True, "initial_peace": 1.0, "tribute_rate": 0.05})
            self.engine.setup(num_consumers=100, num_producers=10, network_type="small-world")
        else:
            self.engine = SimulationEngine(config={})
            ScenarioManager.apply_scenario(self.engine, self.current_scenario)


state = GlobalState()


def generate_plotly_charts(tick_log, engine):
    if not tick_log:
        return "<div class='text-gray-500 text-center p-8'>Simulation not started yet. Run ticks to see real-time price trend!</div>"

    ticks = [d["tick"] for d in tick_log]
    prices = [d["price"] for d in tick_log]
    gini = [d.get("gini_index", 0.0) for d in tick_log]
    herd = [d.get("herd_effect", 0.0) for d in tick_log]

    # Price chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ticks, y=prices, mode='lines+markers', name='Price', line=dict(color='#2196F3', width=2)))
    fig.update_layout(
        title="Emergent Market Price",
        xaxis_title="Ticks",
        yaxis_title="Price",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40),
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    price_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # Gini inequality & Herd Effect chart
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=ticks, y=gini, mode='lines', name='Gini Index (Inequality)', line=dict(color='#E91E63', width=2)))
    fig2.add_trace(go.Scatter(x=ticks, y=herd, mode='lines', name='Herd Effect (Co-movement)', line=dict(color='#4CAF50', width=2)))
    fig2.update_layout(
        title="Socio-Economic Co-evolution Metrics",
        xaxis_title="Ticks",
        yaxis_title="Metric Value",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    metrics_html = fig2.to_html(full_html=False, include_plotlyjs=False)

    return price_html + "<div class='my-6 border-t border-gray-700/50'></div>" + metrics_html


def get_dashboard_html():
    summary = state.engine.get_summary()
    tick_log = state.tick_log

    charts_html = generate_plotly_charts(tick_log, state.engine)

    last_tick_data = tick_log[-1] if tick_log else {}
    current_price = summary["market"].get("current_price", 10.0)
    avg_price = summary["market"].get("avg_price", 10.0)
    volatility = summary["market"].get("price_volatility", 0.0)
    transactions = summary["transactions_total"]

    gini_index = last_tick_data.get("gini_index", 0.0)
    herd_effect = last_tick_data.get("herd_effect", 0.0)
    sentiment_propagation = last_tick_data.get("sentiment_propagation", 0.0)

    social_peace = last_tick_data.get("social_peace", "N/A")
    total_debt = last_tick_data.get("total_debt", "N/A")
    defaults = last_tick_data.get("defaults_count", "N/A")

    scenarios_options = "".join([
        f"<option value='{sc}' {'selected' if state.current_scenario == sc else ''}>{sc}</option>"
        for sc in ["Default ABM"] + ScenarioManager.get_available_scenarios()
    ])

    # Dynamic target ID for whole page refresh on HTMX
    html_content = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EconNet — Interactive Dashboard</title>
        <script src="https://unpkg.com/htmx.org@1.9.10"></script>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-gray-100 min-h-screen" id="dashboard-wrapper">
        <div class="container mx-auto px-4 py-6">
            <!-- Header -->
            <header class="flex flex-col md:flex-row justify-between items-center mb-8 border-b border-gray-800 pb-4">
                <div>
                    <h1 class="text-3xl font-extrabold text-blue-500">EconNet Dashboard</h1>
                    <p class="text-gray-400">Agent-Based Complex Economic Simulation (ABM + AI)</p>
                </div>
                <div class="mt-4 md:mt-0 flex items-center space-x-3">
                    <span class="bg-gray-800 text-blue-400 text-sm font-semibold px-3 py-1.5 rounded-full border border-gray-700">
                        Scenario: <strong id="scenario-badge">{state.current_scenario}</strong>
                    </span>
                    <span class="bg-gray-800 text-green-400 text-sm font-semibold px-3 py-1.5 rounded-full border border-gray-700">
                        Ticks: <strong id="ticks-badge">{len(state.tick_log)}</strong>
                    </span>
                </div>
            </header>

            <!-- Dashboard Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Sidebar Controls & Config -->
                <div class="space-y-6 lg:col-span-1">
                    <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
                        <h2 class="text-xl font-bold mb-4 text-blue-400 flex items-center">
                            🔧 Simulation Controls
                        </h2>

                        <div class="mb-4">
                            <label class="block text-sm font-semibold mb-2 text-gray-300">Select Scenario Preset</label>
                            <select id="scenario-selector" name="scenario"
                                    class="w-full bg-gray-700 text-white rounded px-3 py-2 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    hx-post="/select_scenario" hx-target="#dashboard-wrapper" hx-swap="outerHTML">
                                {scenarios_options}
                            </select>
                        </div>

                        <div class="flex flex-col space-y-2 mt-6">
                            <button hx-post="/step/1" hx-target="#dashboard-wrapper" hx-swap="outerHTML"
                                    class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 px-4 rounded transition duration-200 shadow-md">
                                Run 1 Tick
                            </button>
                            <button hx-post="/step/10" hx-target="#dashboard-wrapper" hx-swap="outerHTML"
                                    class="bg-green-600 hover:bg-green-700 text-white font-bold py-2.5 px-4 rounded transition duration-200 shadow-md">
                                Run 10 Ticks
                            </button>
                            <button hx-post="/step/50" hx-target="#dashboard-wrapper" hx-swap="outerHTML"
                                    class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2.5 px-4 rounded transition duration-200 shadow-md">
                                Run 50 Ticks
                            </button>
                            <button hx-post="/reset" hx-target="#dashboard-wrapper" hx-swap="outerHTML"
                                    class="bg-red-600 hover:bg-red-700 text-white font-bold py-2.5 px-4 rounded transition duration-200 shadow-md">
                                Reset Simulation
                            </button>
                        </div>
                    </div>

                    <!-- Network Status -->
                    <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
                        <h2 class="text-xl font-bold mb-4 text-pink-500">🕸️ Network Graph Metrics</h2>
                        <div class="space-y-3">
                            <div class="flex justify-between border-b border-gray-700 pb-2">
                                <span class="text-gray-400">Total Nodes:</span>
                                <span class="font-bold">{summary["consumers"] + summary["producers"]}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-700 pb-2">
                                <span class="text-gray-400">Total Edges:</span>
                                <span class="font-bold">{summary["network_edges"]}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-700 pb-2">
                                <span class="text-gray-400">Network Density:</span>
                                <span class="font-bold">{summary["network_density"]}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-700 pb-2">
                                <span class="text-gray-400">Avg Clustering Coefficient:</span>
                                <span class="font-bold">{summary["avg_clustering"]}</span>
                            </div>
                            <div class="flex justify-between border-b border-gray-700 pb-2">
                                <span class="text-gray-400">Herd Effect (Co-movement):</span>
                                <span class="font-bold text-pink-400">{herd_effect}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-400">Sentiment Propagation:</span>
                                <span class="font-bold text-pink-400">{sentiment_propagation}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Live Visualizations and charts -->
                <div class="lg:col-span-2 space-y-6">
                    <!-- Stats Grid -->
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-gray-800 p-4 rounded-xl border border-gray-700 text-center">
                            <div class="text-xs text-gray-400 uppercase font-bold mb-1">Current Price</div>
                            <div class="text-2xl font-extrabold text-blue-400">{current_price:.2f}</div>
                        </div>
                        <div class="bg-gray-800 p-4 rounded-xl border border-gray-700 text-center">
                            <div class="text-xs text-gray-400 uppercase font-bold mb-1">Price Volatility</div>
                            <div class="text-2xl font-extrabold text-yellow-500">{volatility:.4f}</div>
                        </div>
                        <div class="bg-gray-800 p-4 rounded-xl border border-gray-700 text-center">
                            <div class="text-xs text-gray-400 uppercase font-bold mb-1">Inequality (Gini)</div>
                            <div class="text-2xl font-extrabold text-pink-500">{gini_index:.3f}</div>
                        </div>
                        <div class="bg-gray-800 p-4 rounded-xl border border-gray-700 text-center">
                            <div class="text-xs text-gray-400 uppercase font-bold mb-1">Transactions</div>
                            <div class="text-2xl font-extrabold text-green-400">{transactions}</div>
                        </div>
                    </div>

                    <!-- Graeberian Stats Card if active -->
                    {f"""
                    <div class="bg-gray-800 p-6 rounded-xl border border-purple-700/50 shadow-md">
                        <h3 class="text-lg font-bold text-purple-400 mb-3">💜 Graeberian Credit Metrics</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-gray-700 p-3 rounded border border-purple-900/40">
                                <span class="text-xs text-gray-400 block mb-1">Social Peace/Trust</span>
                                <span class="text-xl font-bold text-purple-300">{social_peace}</span>
                            </div>
                            <div class="bg-gray-700 p-3 rounded border border-purple-900/40">
                                <span class="text-xs text-gray-400 block mb-1">Total Pending Debt</span>
                                <span class="text-xl font-bold text-pink-400">{total_debt}</span>
                            </div>
                            <div class="bg-gray-700 p-3 rounded border border-purple-900/40">
                                <span class="text-xs text-gray-400 block mb-1">Bad Debt Defaults</span>
                                <span class="text-xl font-bold text-red-400">{defaults}</span>
                            </div>
                        </div>
                    </div>
                    """ if state.engine.graeber_active else ""}

                    <!-- Interactive Chart Container -->
                    <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg min-h-[400px]">
                        <h2 class="text-xl font-bold mb-4 text-blue-400">📈 Live Visualization Charts</h2>
                        <div id="plotly-charts">
                            {charts_html}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return HTMLResponse(content=get_dashboard_html())


@app.post("/select_scenario", response_class=HTMLResponse)
async def post_select_scenario(scenario: str = Form(...)):
    state.current_scenario = scenario
    state.reset()
    return HTMLResponse(content=get_dashboard_html())


@app.post("/step/{count}", response_class=HTMLResponse)
async def post_step(count: int):
    new_ticks = state.engine.run(max_ticks=count)
    state.tick_log.extend(new_ticks)
    return HTMLResponse(content=get_dashboard_html())


@app.post("/reset", response_class=HTMLResponse)
async def post_reset():
    state.reset()
    return HTMLResponse(content=get_dashboard_html())
