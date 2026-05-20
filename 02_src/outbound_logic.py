# 02_src/outbound_logic.py

def calculate_churn_risk(delay_days, stockout_cliff, base_risk=0.02):
    """
    Calculates the probability of client abandonment based on days without inventory.
    Assumes SME landscape where goods are easily substitutable.
    """
    if delay_days <= stockout_cliff:
        return base_risk
        
    days_in_stockout = delay_days - stockout_cliff
    escalation = days_in_stockout / 30.0
    
    final_risk = base_risk + escalation
    return min(0.95, final_risk)

def calculate_sla_penalties(delay_days, grace_period, daily_penalty, order_value):
    """Calculates standard SLA bleeding, capped at the total order value."""
    days_penalized = max(0, delay_days - grace_period)
    return min(days_penalized * daily_penalty, order_value)

def evaluate_freight_strategy(order_value, clv, standard_delay, premium_delay, 
                              grace_period, buffer_days, daily_penalty, 
                              standard_freight_cost, premium_freight_upgrade_cost):
    """
    Evaluates the micro-economics of logistics fulfillment.
    """
    stockout_cliff = buffer_days + grace_period
    
    # --- Standard Route Baseline ---
    std_penalties = calculate_sla_penalties(standard_delay, grace_period, daily_penalty, order_value)
    std_total_delivery_cost = standard_freight_cost + std_penalties
    std_net_revenue = order_value - std_total_delivery_cost
    std_margin = std_net_revenue / order_value if order_value > 0 else 0
    std_churn = calculate_churn_risk(standard_delay, stockout_cliff)
    
    # --- Premium Route Mitigation ---
    prem_total_freight = standard_freight_cost + premium_freight_upgrade_cost
    prem_penalties = calculate_sla_penalties(premium_delay, grace_period, daily_penalty, order_value)
    prem_total_delivery_cost = prem_total_freight + prem_penalties
    prem_net_revenue = order_value - prem_total_delivery_cost
    prem_margin = prem_net_revenue / order_value if order_value > 0 else 0
    prem_churn = calculate_churn_risk(premium_delay, stockout_cliff)
    
    # --- Mitigation ROI ---
    avoided_penalties = std_penalties - prem_penalties
    mitigation_roi = avoided_penalties - premium_freight_upgrade_cost
    
    return {
        "standard": {
            "delivery_cost": std_total_delivery_cost,
            "net_revenue": std_net_revenue,
            "margin": std_margin,
            "churn_risk": std_churn,
            "clv_exposure": clv * std_churn
        },
        "premium": {
            "delivery_cost": prem_total_delivery_cost,
            "net_revenue": prem_net_revenue,
            "margin": prem_margin,
            "churn_risk": prem_churn,
            "clv_exposure": clv * prem_churn
        },
        "roi": mitigation_roi
    }

def evaluate_mitigation_viability(premium_net_revenue, premium_margin, premium_churn, user_mam_threshold):
    """
    Evaluates if the Premium Freight strategy is viable, or if the system 
    must mandate a strategic pivot evaluation.
    """
    is_churn_critical = premium_churn > 0.50
    is_margin_unacceptable = premium_margin < user_mam_threshold
    is_absolute_loss = premium_net_revenue < 0

    requires_pivot_escalation = is_churn_critical or is_margin_unacceptable or is_absolute_loss
    
    return {
        "requires_escalation": requires_pivot_escalation,
        "alerts": {
            "churn_critical": is_churn_critical,
            "margin_breach": is_margin_unacceptable,
            "absolute_loss": is_absolute_loss
        }
    }