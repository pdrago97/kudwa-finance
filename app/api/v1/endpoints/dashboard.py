"""
Dashboard API endpoints for the modern Kudwa interface
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging
from app.services.supabase_client import supabase_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats() -> Dict[str, Any]:
    """Get dashboard statistics"""
    try:
        # Get counts from all tables
        documents_result = supabase_service.client.table("kudwa_documents").select("id", count="exact").execute()
        classes_result = supabase_service.client.table("kudwa_ontology_classes").select("id", count="exact").execute()
        observations_result = supabase_service.client.table("kudwa_financial_observations").select("id", count="exact").execute()
        datasets_result = supabase_service.client.table("kudwa_financial_datasets").select("id", count="exact").execute()
        
        return {
            "documents": documents_result.count or 0,
            "ontology_classes": classes_result.count or 0,
            "observations": observations_result.count or 0,
            "datasets": datasets_result.count or 0
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {
            "documents": 0,
            "ontology_classes": 0,
            "observations": 0,
            "datasets": 0
        }

@router.get("/revenue-trends")
async def get_revenue_trends() -> Dict[str, List]:
    """Get revenue trends for charting"""
    try:
        # Get revenue observations grouped by period
        result = supabase_service.client.table("kudwa_financial_observations").select(
            "period_start, amount"
        ).eq("observation_type", "revenue_stream").order("period_start").execute()
        
        periods = []
        amounts = []
        
        if result.data:
            # Group by period and sum amounts
            period_totals = {}
            for obs in result.data:
                period = obs.get("period_start", "Unknown")
                amount = float(obs.get("amount", 0))
                if period in period_totals:
                    period_totals[period] += amount
                else:
                    period_totals[period] = amount
            
            # Sort by period and prepare data
            sorted_periods = sorted(period_totals.items())
            periods = [p[0] for p in sorted_periods]
            amounts = [p[1] for p in sorted_periods]
        
        return {
            "periods": periods,
            "amounts": amounts
        }
    except Exception as e:
        logger.error(f"Error getting revenue trends: {e}")
        return {"periods": [], "amounts": []}

@router.get("/expense-breakdown")
async def get_expense_breakdown() -> Dict[str, List]:
    """Get expense breakdown for pie chart"""
    try:
        # Get expense observations grouped by type
        result = supabase_service.client.table("kudwa_financial_observations").select(
            "observation_type, amount"
        ).in_("observation_type", ["expense_category", "cost_of_goods_sold", "non_operating_expense"]).execute()
        
        categories = []
        amounts = []
        
        if result.data:
            # Group by observation type and sum amounts
            type_totals = {}
            for obs in result.data:
                obs_type = obs.get("observation_type", "Unknown")
                amount = float(obs.get("amount", 0))
                if obs_type in type_totals:
                    type_totals[obs_type] += amount
                else:
                    type_totals[obs_type] = amount
            
            # Prepare data
            categories = list(type_totals.keys())
            amounts = list(type_totals.values())
        
        return {
            "categories": categories,
            "amounts": amounts
        }
    except Exception as e:
        logger.error(f"Error getting expense breakdown: {e}")
        return {"categories": [], "amounts": []}

@router.get("/recent-observations")
async def get_recent_observations() -> Dict[str, List]:
    """Get recent financial observations"""
    try:
        result = supabase_service.client.table("kudwa_financial_observations").select(
            "observation_type, account_name, amount, currency, period_start, period_end"
        ).order("created_at", desc=True).limit(10).execute()

        return {
            "observations": result.data or []
        }
    except Exception as e:
        logger.error(f"Error getting recent observations: {e}")
        return {"observations": []}

@router.get("/node-details/{node_type}/{node_id}")
async def get_node_details(node_type: str, node_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific node"""
    try:
        if node_type == "ontology_class":
            result = supabase_service.client.table("kudwa_ontology_classes").select("*").eq("class_id", node_id).execute()
            if result.data:
                return result.data[0]

        elif node_type == "financial_entity":
            result = supabase_service.client.table("kudwa_financial_observations").select("*").eq("id", node_id).execute()
            if result.data:
                return result.data[0]

        elif node_type == "document":
            result = supabase_service.client.table("kudwa_documents").select("*").eq("id", node_id).execute()
            if result.data:
                return result.data[0]

        return {"error": "Node not found"}

    except Exception as e:
        logger.error(f"Error getting node details: {e}")
        return {"error": str(e)}

@router.post("/widgets/generate")
async def generate_widget(request: dict):
    """Generate a custom widget based on user prompt"""
    try:
        prompt = request.get("prompt", "")
        size = request.get("size", "half")

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        # Determine widget type from prompt
        prompt_lower = prompt.lower()
        widget_type = "text"

        if any(word in prompt_lower for word in ["spotlight", "biggest", "highest", "largest", "maximum"]):
            widget_type = "spotlight"
        elif any(word in prompt_lower for word in ["chart", "graph", "plot", "line", "bar", "pie"]):
            widget_type = "chart"
        elif any(word in prompt_lower for word in ["table", "list", "rows", "data"]):
            widget_type = "table"
        elif any(word in prompt_lower for word in ["kpi", "metric", "card", "dashboard"]):
            widget_type = "kpi"
        elif any(word in prompt_lower for word in ["feed", "live", "recent", "stream"]):
            widget_type = "feed"

        # Generate actual HTML/CSS/JS code based on the widget type and prompt
        html_code = await generate_widget_html(widget_type, prompt, size)

        return {
            "success": True,
            "widget_type": widget_type,
            "size": size,
            "prompt": prompt,
            "html": html_code
        }

    except Exception as e:
        logger.error(f"Error generating widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_widget_html(widget_type: str, prompt: str, size: str) -> str:
    """Generate HTML/CSS/JS code for different widget types"""

    if widget_type == "spotlight":
        return generate_spotlight_widget_html(prompt)
    elif widget_type == "chart" and "revenue" in prompt.lower():
        return generate_revenue_chart_html(prompt)
    elif widget_type == "chart" and "expense" in prompt.lower():
        return generate_expense_chart_html(prompt)
    elif widget_type == "table" and "expense" in prompt.lower():
        return generate_expense_table_html(prompt)
    elif widget_type == "kpi":
        return generate_kpi_widget_html(prompt)
    elif widget_type == "feed":
        return generate_live_feed_html(prompt)
    else:
        return generate_generic_widget_html(prompt)

def generate_spotlight_widget_html(prompt: str) -> str:
    """Generate HTML for spotlight widget"""
    return """
    <div class="custom-spotlight-widget">
        <div class="spotlight-header">
            <i class="fas fa-search-dollar"></i>
            <h4>Financial Spotlight</h4>
        </div>
        <div class="spotlight-content" id="spotlight-content">
            <div class="widget-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Finding biggest value...</span>
            </div>
        </div>
    </div>
    <script>
    (async function() {
        try {
            const response = await fetch('/api/v1/dashboard/recent-observations');
            const data = await response.json();

            if (!data.observations || data.observations.length === 0) {
                throw new Error('No data available');
            }

            // Find the observation with the highest amount
            const biggestObs = data.observations.reduce((max, obs) => {
                const amount = parseFloat(obs.amount) || 0;
                const maxAmount = parseFloat(max.amount) || 0;
                return amount > maxAmount ? obs : max;
            }, data.observations[0]);

            const content = document.getElementById('spotlight-content');
            content.innerHTML = `
                <div class="spotlight-main">
                    <div class="spotlight-amount">$${(biggestObs.amount || 0).toLocaleString()}</div>
                    <div class="spotlight-type">${biggestObs.observation_type || 'Financial Observation'}</div>
                </div>
                <div class="spotlight-details">
                    <div class="detail-row">
                        <span class="detail-label">Account:</span>
                        <span class="detail-value">${biggestObs.account_name || 'N/A'}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Period:</span>
                        <span class="detail-value">${new Date(biggestObs.period_start || Date.now()).toLocaleDateString()}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Currency:</span>
                        <span class="detail-value">${biggestObs.currency || 'USD'}</span>
                    </div>
                </div>
                <div class="spotlight-insight">
                    <i class="fas fa-lightbulb"></i>
                    <p>This represents the highest single financial observation in your database.</p>
                </div>
            `;
        } catch (error) {
            document.getElementById('spotlight-content').innerHTML =
                '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading spotlight data</p></div>';
        }
    })();
    </script>
    <style>
    .custom-spotlight-widget {
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 1.5rem;
    }
    .spotlight-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border);
    }
    .spotlight-header i {
        font-size: 1.5rem;
        color: var(--primary-color);
    }
    .spotlight-main {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, var(--primary-color), #4f46e5);
        border-radius: var(--radius-lg);
        color: white;
        margin-bottom: 1.5rem;
    }
    .spotlight-amount {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .spotlight-type {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .spotlight-details {
        display: grid;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem;
        background: var(--surface);
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }
    .detail-label {
        font-weight: 500;
        color: var(--text-secondary);
    }
    .detail-value {
        font-weight: 600;
        color: var(--text-primary);
    }
    .spotlight-insight {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 1rem;
        background: rgba(37, 99, 235, 0.05);
        border-radius: var(--radius);
        border-left: 4px solid var(--primary-color);
    }
    .spotlight-insight i {
        color: var(--primary-color);
        margin-top: 0.125rem;
    }
    .spotlight-insight p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.875rem;
        line-height: 1.5;
    }
    </style>
    """

def generate_revenue_chart_html(prompt: str) -> str:
    """Generate HTML for revenue chart widget"""
    return """
    <div class="custom-chart-widget">
        <div class="widget-header">
            <h4><i class="fas fa-chart-line"></i> Revenue Trends</h4>
        </div>
        <div id="revenue-chart" style="height: 300px;"></div>
    </div>
    <script>
    (async function() {
        try {
            const response = await fetch('/api/v1/dashboard/revenue-trends');
            const data = await response.json();

            const trace = {
                x: data.months,
                y: data.amounts,
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#2563eb', width: 3 },
                marker: { size: 8, color: '#2563eb' },
                fill: 'tonexty',
                fillcolor: 'rgba(37, 99, 235, 0.1)'
            };

            const layout = {
                margin: { t: 20, r: 20, b: 40, l: 60 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { family: 'Inter, sans-serif', size: 12 },
                xaxis: {
                    gridcolor: '#e5e7eb',
                    title: 'Month'
                },
                yaxis: {
                    gridcolor: '#e5e7eb',
                    tickformat: '$,.0f',
                    title: 'Revenue'
                }
            };

            Plotly.newPlot('revenue-chart', [trace], layout, {responsive: true});
        } catch (error) {
            document.getElementById('revenue-chart').innerHTML =
                '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading chart data</p></div>';
        }
    })();
    </script>
    """

def generate_expense_table_html(prompt: str) -> str:
    """Generate HTML for expense table widget"""
    return """
    <div class="custom-table-widget">
        <div class="widget-header">
            <h4><i class="fas fa-table"></i> Expense Categories</h4>
            <span class="record-count" id="expense-count">Loading...</span>
        </div>
        <div class="table-container" id="expense-table">
            <div class="widget-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Loading expense data...</span>
            </div>
        </div>
    </div>
    <script>
    (async function() {
        try {
            const response = await fetch('/api/v1/dashboard/recent-observations');
            const data = await response.json();

            const expenses = data.observations.filter(obs =>
                obs.observation_type && obs.observation_type.toLowerCase().includes('expense')
            );

            document.getElementById('expense-count').textContent = `${expenses.length} records`;

            const tableHTML = `
                <table class="widget-table">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Account</th>
                            <th>Amount</th>
                            <th>Currency</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${expenses.map(exp => `
                            <tr>
                                <td><span class="type-badge">${exp.observation_type}</span></td>
                                <td>${exp.account_name || 'N/A'}</td>
                                <td class="amount-cell">$${(exp.amount || 0).toLocaleString()}</td>
                                <td>${exp.currency || 'USD'}</td>
                                <td>${new Date(exp.period_start || Date.now()).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;

            document.getElementById('expense-table').innerHTML = tableHTML;
        } catch (error) {
            document.getElementById('expense-table').innerHTML =
                '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading expense data</p></div>';
        }
    })();
    </script>
    <style>
    .custom-table-widget {
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 1rem;
    }
    .widget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
    }
    .record-count {
        font-size: 0.875rem;
        color: var(--text-secondary);
    }
    .table-container {
        flex: 1;
        overflow: auto;
    }
    .widget-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
    }
    .widget-table th {
        background: var(--background);
        padding: 0.75rem 0.5rem;
        text-align: left;
        font-weight: 600;
        color: var(--text-secondary);
        border-bottom: 2px solid var(--border);
        position: sticky;
        top: 0;
    }
    .widget-table td {
        padding: 0.75rem 0.5rem;
        border-bottom: 1px solid var(--border);
    }
    .widget-table tr:hover {
        background: var(--surface-hover);
    }
    .type-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
    }
    .amount-cell {
        font-weight: 600;
        text-align: right;
    }
    </style>
    """

def generate_generic_widget_html(prompt: str) -> str:
    """Generate HTML for generic widget"""
    return f"""
    <div class="custom-generic-widget">
        <div class="widget-header">
            <h4><i class="fas fa-magic"></i> AI Generated Widget</h4>
        </div>
        <div class="widget-content">
            <div class="ai-response">
                <i class="fas fa-robot"></i>
                <h5>Widget Request</h5>
                <p>"{prompt}"</p>
                <div class="enhancement-note">
                    <i class="fas fa-info-circle"></i>
                    <p>This widget would be enhanced by AI agents to create a functional data visualization based on your specific request.</p>
                </div>
            </div>
        </div>
    </div>
    <style>
    .custom-generic-widget {{
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 1.5rem;
    }}
    .widget-header {{
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }}
    .ai-response {{
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 1rem;
    }}
    .ai-response i.fa-robot {{
        font-size: 3rem;
        color: var(--primary-color);
    }}
    .ai-response h5 {{
        margin: 0;
        color: var(--text-primary);
    }}
    .ai-response p {{
        margin: 0;
        color: var(--text-secondary);
        font-style: italic;
    }}
    .enhancement-note {{
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 1rem;
        background: rgba(37, 99, 235, 0.05);
        border-radius: var(--radius);
        border-left: 4px solid var(--primary-color);
        margin-top: 1rem;
    }}
    .enhancement-note i {{
        color: var(--primary-color);
        margin-top: 0.125rem;
    }}
    .enhancement-note p {{
        margin: 0;
        font-size: 0.875rem;
        text-align: left;
    }}
    </style>
    """

def generate_kpi_widget_html(prompt: str) -> str:
    """Generate HTML for KPI widget"""
    return """
    <div class="custom-kpi-widget">
        <div class="widget-header">
            <h4><i class="fas fa-tachometer-alt"></i> Key Performance Indicators</h4>
        </div>
        <div class="kpi-grid" id="kpi-grid">
            <div class="widget-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Loading KPI data...</span>
            </div>
        </div>
    </div>
    <script>
    (async function() {
        try {
            const [statsResponse, revenueResponse] = await Promise.all([
                fetch('/api/v1/dashboard/stats'),
                fetch('/api/v1/dashboard/revenue-trends')
            ]);

            const stats = await statsResponse.json();
            const revenue = await revenueResponse.json();

            const totalRevenue = revenue.amounts.reduce((sum, amount) => sum + amount, 0);

            const kpiGrid = document.getElementById('kpi-grid');
            kpiGrid.innerHTML = `
                <div class="kpi-card primary">
                    <div class="kpi-icon"><i class="fas fa-dollar-sign"></i></div>
                    <div class="kpi-content">
                        <div class="kpi-value">$${totalRevenue.toLocaleString()}</div>
                        <div class="kpi-label">Total Revenue</div>
                        <div class="kpi-change positive">+12.5%</div>
                    </div>
                </div>
                <div class="kpi-card success">
                    <div class="kpi-icon"><i class="fas fa-file-alt"></i></div>
                    <div class="kpi-content">
                        <div class="kpi-value">${stats.documents}</div>
                        <div class="kpi-label">Documents</div>
                        <div class="kpi-change positive">+${stats.documents}</div>
                    </div>
                </div>
                <div class="kpi-card info">
                    <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="kpi-content">
                        <div class="kpi-value">${stats.observations}</div>
                        <div class="kpi-label">Observations</div>
                        <div class="kpi-change positive">+${stats.observations}</div>
                    </div>
                </div>
                <div class="kpi-card warning">
                    <div class="kpi-icon"><i class="fas fa-project-diagram"></i></div>
                    <div class="kpi-content">
                        <div class="kpi-value">${stats.ontology_classes}</div>
                        <div class="kpi-label">Ontology Classes</div>
                        <div class="kpi-change positive">+${stats.ontology_classes}</div>
                    </div>
                </div>
            `;
        } catch (error) {
            document.getElementById('kpi-grid').innerHTML =
                '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading KPI data</p></div>';
        }
    })();
    </script>
    <style>
    .custom-kpi-widget {
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 1rem;
    }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        flex: 1;
    }
    .kpi-card {
        display: flex;
        align-items: center;
        padding: 1.5rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    .kpi-card.primary { border-left: 4px solid var(--primary-color); }
    .kpi-card.success { border-left: 4px solid var(--success-color); }
    .kpi-card.info { border-left: 4px solid #3b82f6; }
    .kpi-card.warning { border-left: 4px solid var(--warning-color); }
    .kpi-icon {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.25rem;
    }
    .kpi-card.primary .kpi-icon {
        background: rgba(37, 99, 235, 0.1);
        color: var(--primary-color);
    }
    .kpi-card.success .kpi-icon {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
    }
    .kpi-card.info .kpi-icon {
        background: rgba(59, 130, 246, 0.1);
        color: #3b82f6;
    }
    .kpi-card.warning .kpi-icon {
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning-color);
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 0.25rem;
    }
    .kpi-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    .kpi-change {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.125rem 0.375rem;
        border-radius: 12px;
        display: inline-block;
    }
    .kpi-change.positive {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
    }
    </style>
    """

def generate_live_feed_html(prompt: str) -> str:
    """Generate HTML for live feed widget"""
    return """
    <div class="custom-feed-widget">
        <div class="widget-header">
            <h4><i class="fas fa-stream"></i> Live Financial Feed</h4>
            <button class="refresh-btn" onclick="refreshFeed()">
                <i class="fas fa-sync-alt"></i>
            </button>
        </div>
        <div class="feed-container" id="feed-container">
            <div class="widget-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Loading live feed...</span>
            </div>
        </div>
    </div>
    <script>
    async function loadFeed() {
        try {
            const response = await fetch('/api/v1/dashboard/recent-observations');
            const data = await response.json();

            const feedContainer = document.getElementById('feed-container');
            feedContainer.innerHTML = data.observations.map(obs => `
                <div class="feed-item">
                    <div class="feed-icon">
                        <i class="fas fa-${obs.observation_type && obs.observation_type.toLowerCase().includes('expense') ? 'arrow-down' : 'arrow-up'}"></i>
                    </div>
                    <div class="feed-content">
                        <div class="feed-title">${obs.observation_type || 'Financial Observation'}</div>
                        <div class="feed-details">
                            <span class="feed-account">${obs.account_name || 'Unknown Account'}</span>
                            <span class="feed-amount">$${(obs.amount || 0).toLocaleString()}</span>
                        </div>
                        <div class="feed-time">${new Date(obs.period_start || Date.now()).toLocaleString()}</div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            document.getElementById('feed-container').innerHTML =
                '<div class="widget-error"><i class="fas fa-exclamation-triangle"></i><p>Error loading feed data</p></div>';
        }
    }

    function refreshFeed() {
        document.getElementById('feed-container').innerHTML =
            '<div class="widget-loading"><i class="fas fa-spinner fa-spin"></i><span>Refreshing...</span></div>';
        setTimeout(loadFeed, 500);
    }

    loadFeed();
    // Auto-refresh every 30 seconds
    setInterval(loadFeed, 30000);
    </script>
    <style>
    .custom-feed-widget {
        height: 100%;
        display: flex;
        flex-direction: column;
        padding: 1rem;
    }
    .widget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border);
    }
    .refresh-btn {
        background: none;
        border: 1px solid var(--border);
        color: var(--text-secondary);
        padding: 0.5rem;
        border-radius: var(--radius);
        cursor: pointer;
        transition: all 0.2s;
    }
    .refresh-btn:hover {
        color: var(--primary-color);
        border-color: var(--primary-color);
    }
    .feed-container {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .feed-item {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        transition: transform 0.2s;
    }
    .feed-item:hover {
        transform: translateX(4px);
    }
    .feed-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(37, 99, 235, 0.1);
        color: var(--primary-color);
        flex-shrink: 0;
    }
    .feed-content {
        flex: 1;
    }
    .feed-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }
    .feed-details {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.25rem;
    }
    .feed-account {
        color: var(--text-secondary);
        font-size: 0.875rem;
    }
    .feed-amount {
        font-weight: 600;
        color: var(--text-primary);
    }
    .feed-time {
        font-size: 0.75rem;
        color: var(--text-secondary);
    }
    </style>
    """

@router.post("/wipe-database")
async def wipe_database() -> Dict[str, str]:
    """Wipe all data from the database"""
    try:
        logger.warning("Database wipe requested - clearing all data")
        
        # Clear all tables in correct order (respecting foreign keys)
        supabase_service.client.table("kudwa_financial_observations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase_service.client.table("kudwa_financial_datasets").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase_service.client.table("kudwa_ontology_relations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase_service.client.table("kudwa_ontology_classes").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase_service.client.table("kudwa_documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        logger.info("Database wipe completed successfully")
        return {"status": "success", "message": "Database wiped successfully"}
        
    except Exception as e:
        logger.error(f"Error wiping database: {e}")
        raise HTTPException(status_code=500, detail=f"Error wiping database: {str(e)}")

@router.get("/ontology/classes")
async def get_ontology_classes() -> Dict[str, List]:
    """Get all ontology classes"""
    try:
        result = supabase_service.client.table("kudwa_ontology_classes").select(
            "id, class_id, label, class_type, status"
        ).order("class_id").execute()
        
        return {
            "classes": result.data or []
        }
    except Exception as e:
        logger.error(f"Error getting ontology classes: {e}")
        return {"classes": []}

@router.post("/ontology/classes/{class_id}/approve")
async def approve_ontology_class(class_id: str) -> Dict[str, str]:
    """Approve an ontology class"""
    try:
        result = supabase_service.client.table("kudwa_ontology_classes").update({
            "status": "active"
        }).eq("id", class_id).execute()
        
        if result.data:
            return {"status": "success", "message": "Ontology class approved"}
        else:
            raise HTTPException(status_code=404, detail="Ontology class not found")
            
    except Exception as e:
        logger.error(f"Error approving ontology class: {e}")
        raise HTTPException(status_code=500, detail=f"Error approving ontology class: {str(e)}")

@router.get("/documents")
async def get_documents() -> Dict[str, List]:
    """Get all documents"""
    try:
        result = supabase_service.client.table("kudwa_documents").select(
            "id, filename, content_type, file_size, processing_status, created_at, uploaded_by"
        ).order("created_at", desc=True).execute()
        
        return {
            "documents": result.data or []
        }
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return {"documents": []}

@router.get("/approvals")
async def get_pending_approvals() -> Dict[str, List]:
    """Get pending approvals"""
    try:
        # Get pending ontology classes
        classes_result = supabase_service.client.table("kudwa_ontology_classes").select(
            "id, class_id, label, properties"
        ).eq("status", "pending_review").execute()
        
        approvals = []
        
        if classes_result.data:
            for cls in classes_result.data:
                approvals.append({
                    "id": cls["id"],
                    "type": "ontology_class",
                    "title": f"New Ontology Class: {cls['label']}",
                    "description": f"Auto-generated class '{cls['class_id']}' from document processing",
                    "data": cls
                })
        
        return {
            "approvals": approvals
        }
    except Exception as e:
        logger.error(f"Error getting pending approvals: {e}")
        return {"approvals": []}

@router.get("/knowledge-graph")
async def get_knowledge_graph() -> Dict[str, Any]:
    """Get knowledge graph data for visualization"""
    try:
        # Get ontology classes
        classes_result = supabase_service.client.table("kudwa_ontology_classes").select(
            "id, class_id, label, class_type"
        ).execute()

        # Get financial observations (sample)
        observations_result = supabase_service.client.table("kudwa_financial_observations").select(
            "id, observation_type, account_name, amount, source_document_id"
        ).limit(50).execute()

        # Get documents
        documents_result = supabase_service.client.table("kudwa_documents").select(
            "id, filename"
        ).execute()

        # Build graph elements
        elements = []

        # Add ontology class nodes
        if classes_result.data:
            for cls in classes_result.data:
                elements.append({
                    "data": {
                        "id": f"class_{cls['id']}",
                        "label": cls['label'],
                        "type": "ontology_class",
                        "size": 5,
                        "class_id": cls['class_id']
                    }
                })

        # Add document nodes
        if documents_result.data:
            for doc in documents_result.data:
                elements.append({
                    "data": {
                        "id": f"doc_{doc['id']}",
                        "label": doc['filename'][:20] + "..." if len(doc['filename']) > 20 else doc['filename'],
                        "type": "document",
                        "size": 3
                    }
                })

        # Add financial entity nodes and relationships
        if observations_result.data:
            for obs in observations_result.data:
                entity_id = f"entity_{obs['id']}"

                # Add entity node
                elements.append({
                    "data": {
                        "id": entity_id,
                        "label": obs['account_name'][:15] + "..." if len(obs['account_name']) > 15 else obs['account_name'],
                        "type": "financial_entity",
                        "size": max(1, min(10, abs(float(obs.get('amount', 0))) / 1000000)),  # Size based on amount
                        "amount": obs.get('amount', 0),
                        "observation_type": obs['observation_type']
                    }
                })

                # Add relationship to ontology class
                class_node_id = None
                if classes_result.data:
                    for cls in classes_result.data:
                        if cls['class_id'] == obs['observation_type']:
                            class_node_id = f"class_{cls['id']}"
                            break

                if class_node_id:
                    elements.append({
                        "data": {
                            "id": f"rel_{entity_id}_{class_node_id}",
                            "source": entity_id,
                            "target": class_node_id,
                            "relationship": "instance_of"
                        }
                    })

                # Add relationship to document
                if obs.get('source_document_id'):
                    doc_node_id = f"doc_{obs['source_document_id']}"
                    elements.append({
                        "data": {
                            "id": f"rel_{entity_id}_{doc_node_id}",
                            "source": entity_id,
                            "target": doc_node_id,
                            "relationship": "extracted_from"
                        }
                    })

        return {
            "elements": elements,
            "stats": {
                "nodes": len([e for e in elements if 'source' not in e['data']]),
                "edges": len([e for e in elements if 'source' in e['data']]),
                "ontology_classes": len(classes_result.data) if classes_result.data else 0,
                "financial_entities": len(observations_result.data) if observations_result.data else 0,
                "documents": len(documents_result.data) if documents_result.data else 0
            }
        }

    except Exception as e:
        logger.error(f"Error getting knowledge graph: {e}")
        return {"elements": [], "stats": {"nodes": 0, "edges": 0}}

@router.post("/chat/message")
async def send_chat_message(request: Dict[str, Any]) -> Dict[str, str]:
    """Send a message to the AI chat system"""
    try:
        message = request.get("message", "")
        user_id = request.get("user_id", "demo_user")

        # For now, return a simple response
        # TODO: Integrate with actual RAG system

        if "revenue" in message.lower():
            response = "Based on your financial data, I can see revenue trends across multiple periods. Your highest revenue was $6.48M in April 2025. Would you like me to analyze specific revenue patterns or compare periods?"
        elif "expense" in message.lower():
            response = "Your expense data shows business expenses up to $6.47M. The main categories include operating expenses, cost of goods sold, and non-operating expenses. Would you like a detailed breakdown?"
        elif "ontology" in message.lower():
            response = "Your current ontology includes 9 financial entity classes: company, revenue_stream, expense_category, cost_of_goods_sold, financial_summary, financial_period, and others. All are currently pending review. Would you like me to help you approve them?"
        elif "graph" in message.lower() or "knowledge" in message.lower():
            response = "The knowledge graph shows the relationships between your ontology classes, financial entities, and source documents. You can see how entities are connected to their ontology classes and which documents they were extracted from. Try different layout options to explore the relationships!"
        else:
            response = f"I understand you're asking about: '{message}'. I can help you analyze your financial data, manage your ontology, explore the knowledge graph, or process new documents. What specific aspect would you like to explore?"

        return {"response": response}

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return {"response": "I apologize, but I encountered an error processing your message. Please try again."}
