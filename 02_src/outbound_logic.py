def _get_horizon(delay: int, threshold: int) -> str:
    if delay < threshold:
        return f"Tactical Horizon ({threshold - delay} Buffer Days Remaining)"
    elif delay == threshold:
        return "Critical Horizon (Zero Buffer - Arriving Exact Day of Stockout)"
    else:
        return f"Strategic Horizon (Active Stockout: Day {delay - threshold})"

def _calculate_exposure(days_delayed, order_value, annualized_clv, daily_sla_penalty, strategic_threshold, grace_period_days, switching_friction, base_churn_prob):
    billable_late_days = max(0, days_delayed - grace_period_days)
    total_sla_penalty = min(billable_late_days * daily_sla_penalty, order_value)
    
    if days_delayed <= strategic_threshold:
        calculated_churn = base_churn_prob
        clv_exposure = 0.0  
    else:
        days_in_stockout = days_delayed - strategic_threshold
        churn_escalation = (days_in_stockout / 30.0) * (1.0 - switching_friction)
        calculated_churn = min(0.95, base_churn_prob + churn_escalation)
        clv_exposure = annualized_clv * calculated_churn
        
    return {
        "penalty": total_sla_penalty,
        "churn_prob": calculated_churn,
        "clv_exposure": clv_exposure,
        "total_damage": total_sla_penalty + clv_exposure
    }

def evaluate_outbound_resilience(
    order_value: float, annualized_clv: float, standard_freight: float, premium_freight: float,
    standard_delay_days: int, premium_delay_days: int, daily_sla_penalty: float,
    client_buffer_days: int, grace_period_days: int, switching_friction: float,
    base_churn_prob: float = 0.02, alt_market_recovery: float = 0.0
) -> dict:
    
    freight_premium = max(0.0, premium_freight - standard_freight)
    strategic_threshold = client_buffer_days + grace_period_days
    
    std_metrics = _calculate_exposure(standard_delay_days, order_value, annualized_clv, daily_sla_penalty, strategic_threshold, grace_period_days, switching_friction, base_churn_prob)
    prem_metrics = _calculate_exposure(premium_delay_days, order_value, annualized_clv, daily_sla_penalty, strategic_threshold, grace_period_days, switching_friction, base_churn_prob)
    
    total_premium_cost = freight_premium + prem_metrics["total_damage"]
    abandonment_cost = std_metrics["clv_exposure"] - alt_market_recovery

    # ==========================================
    # DECISION ENGINE (BUSINESS RULES ENFORCED)
    # ==========================================
    
    # CASE 1: Standard Route is perfectly safe.
    if standard_delay_days <= strategic_threshold:
        return {
            "action": "ABSORB STANDARD DELAY (NO STOCKOUT RISK)",
            "color": "success", "horizon": _get_horizon(standard_delay_days, strategic_threshold),
            "freight_premium": 0.0, "residual_penalty": std_metrics["penalty"], "value_at_risk": 0.0,
            "net_benefit": 0.0, "threshold_days": strategic_threshold, "calculated_churn": std_metrics["churn_prob"],
            "rationale": "Standard fulfillment arrives before the stockout cliff. Preserve capital."
        }
        
    # CASE 2: Standard breaches, but Premium Freight completely rescues the shipment.
    elif premium_delay_days <= strategic_threshold:
        # NO PIVOT ALLOWED. We successfully protect the client.
        if total_premium_cost < std_metrics["total_damage"]:
            return {
                "action": "EXECUTE PREMIUM FREIGHT (TIMELINE COMPRESSION)",
                "color": "success", "horizon": _get_horizon(premium_delay_days, strategic_threshold),
                "freight_premium": freight_premium, "residual_penalty": prem_metrics["penalty"], 
                "value_at_risk": std_metrics["total_damage"], "net_benefit": std_metrics["total_damage"] - total_premium_cost,
                "threshold_days": strategic_threshold, "calculated_churn": prem_metrics["churn_prob"],
                "rationale": f"Air freight reduces delay to {premium_delay_days} days, rescuing the client from a stockout. USD {freight_premium:,.2f} justified against USD {std_metrics['total_damage']:,.2f} exposure."
            }
        else:
            return {
                "action": "ABSORB STANDARD DELAY (PRESERVE CAPITAL)",
                "color": "warning", "horizon": _get_horizon(standard_delay_days, strategic_threshold),
                "freight_premium": 0.0, "residual_penalty": std_metrics["penalty"], "value_at_risk": std_metrics["total_damage"],
                "net_benefit": total_premium_cost - std_metrics["total_damage"], "threshold_days": strategic_threshold, "calculated_churn": std_metrics["churn_prob"],
                "rationale": f"Standard route damage (USD {std_metrics['total_damage']:,.2f}) is cheaper than the mitigation cost. Absorb the hit."
            }
            
    # CASE 3: Both standard and premium routes result in a stockout. Pivot is on the table.
    else:
        if total_premium_cost < std_metrics["total_damage"] and total_premium_cost < abandonment_cost:
            return {
                "action": "EXECUTE PREMIUM FREIGHT (DAMAGE CONTROL)",
                "color": "warning", "horizon": _get_horizon(premium_delay_days, strategic_threshold),
                "freight_premium": freight_premium, "residual_penalty": prem_metrics["penalty"], 
                "value_at_risk": std_metrics["total_damage"], "net_benefit": std_metrics["total_damage"] - total_premium_cost,
                "threshold_days": strategic_threshold, "calculated_churn": prem_metrics["churn_prob"],
                "rationale": "Premium freight cannot prevent a stockout, but it minimizes SLA fines and churn exposure better than abandoning the client."
            }
        elif std_metrics["total_damage"] <= total_premium_cost and std_metrics["total_damage"] <= abandonment_cost:
            return {
                "action": "ABSORB STANDARD DELAY (CRITICAL EXPOSURE)",
                "color": "error", "horizon": _get_horizon(standard_delay_days, strategic_threshold),
                "freight_premium": 0.0, "residual_penalty": std_metrics["penalty"], "value_at_risk": std_metrics["total_damage"],
                "net_benefit": total_premium_cost - std_metrics["total_damage"], "threshold_days": strategic_threshold, "calculated_churn": std_metrics["churn_prob"],
                "rationale": "All mitigations are too expensive. Absorb full SLA and Churn penalties."
            }
        else:
            return {
                "action": "EXECUTE STRATEGIC PIVOT (REALLOCATE CAPACITY)",
                "color": "error", "horizon": _get_horizon(standard_delay_days, strategic_threshold),
                "freight_premium": 0.0, "residual_penalty": 0.0, "value_at_risk": std_metrics["clv_exposure"],
                "net_benefit": abandonment_cost - total_premium_cost, "threshold_days": strategic_threshold, "calculated_churn": std_metrics["churn_prob"],
                "rationale": f"Mitigation costs are untenable. Accept account loss risk and reallocate to alternative market yielding USD {alt_market_recovery:,.2f}."
            }