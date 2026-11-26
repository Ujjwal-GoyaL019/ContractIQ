from typing import List, Dict, Any, Optional
import time
import math
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds


class SupplierOption:
    def __init__(
        self,
        supplier_id: str,
        supplier_name: str,
        supplier_code: str,
        country: str,
        unit_cost: float,
        surcharge_pct: float = 0.0,
        lead_time_days: int = 14,
        reliability_score: float = 0.95,
        disruption_risk_score: float = 15.0,
        moq: int = 50,
        max_capacity: int = 5000,
        fixed_order_cost: float = 150.0,
        sla_penalty_rate: float = 0.015,
    ):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.supplier_code = supplier_code
        self.country = country
        self.unit_cost = max(0.01, float(unit_cost))
        self.surcharge_pct = max(0.0, float(surcharge_pct))
        self.lead_time_days = max(1, int(lead_time_days))
        self.reliability_score = min(1.0, max(0.05, float(reliability_score)))
        self.disruption_risk_score = min(100.0, max(0.0, float(disruption_risk_score)))
        self.moq = max(0, int(moq))
        self.max_capacity = max(self.moq, int(max_capacity))
        self.fixed_order_cost = max(0.0, float(fixed_order_cost))
        self.sla_penalty_rate = max(0.0, float(sla_penalty_rate))

    @property
    def effective_unit_cost(self) -> float:
        return self.unit_cost * (1.0 + self.surcharge_pct / 100.0)

    @property
    def expected_risk_factor(self) -> float:
        # Combines delivery unreliability (1 - reliability) and geopolitical/port disruption index
        return (1.0 - self.reliability_score) + 0.45 * (self.disruption_risk_score / 100.0)


class MultiSupplierMILPOptimizer:
    """
    Prescriptive Operations Research Engine using Mixed-Integer Linear Programming (SciPy HiGHS MILP).
    Computes optimal multi-supplier order splits minimizing total risk-adjusted procurement cost
    subject to MOQ activation, supplier capacity, and single-source concentration caps.
    """

    @staticmethod
    def solve(
        sku: str,
        total_demand_qty: int,
        suppliers: List[SupplierOption],
        risk_aversion_lambda: float = 1.5,
        max_single_supplier_share: float = 0.70,
        target_lead_time_days: int = 18,
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()

        if total_demand_qty <= 0:
            raise ValueError("total_demand_qty must be a positive integer.")
        if not suppliers:
            raise ValueError("At least one qualified supplier option is required.")

        n = len(suppliers)
        risk_aversion_lambda = max(0.0, min(5.0, float(risk_aversion_lambda)))
        share_cap = max(0.25, min(1.0, float(max_single_supplier_share)))
        solver_notes: List[str] = []

        # Ensure feasibility of concentration cap when supplier count is small
        min_feasible_share = 1.0 / n
        if share_cap < min_feasible_share:
            share_cap = min(1.0, math.ceil(min_feasible_share * 100) / 100.0)
            solver_notes.append(
                f"Relaxed single-supplier share cap to {int(share_cap * 100)}% to maintain feasibility across {n} suppliers."
            )

        # Compute per-unit risk-adjusted objective coefficient for each supplier
        unit_obj_costs = []
        for s in suppliers:
            eff_cost = s.effective_unit_cost
            risk_premium = risk_aversion_lambda * s.expected_risk_factor * eff_cost
            lead_excess = max(0, s.lead_time_days - target_lead_time_days)
            lead_penalty = lead_excess * 0.012 * eff_cost
            unit_obj_costs.append(eff_cost + risk_premium + lead_penalty)

        def _run_milp(cap_ratio: float, enforce_moq: bool = True):
            # Decision vector z = [x_0, ..., x_{n-1}, y_0, ..., y_{n-1}]
            # x_i: integer units ordered from supplier i; y_i: binary indicator whether supplier i is used
            c = np.array(
                unit_obj_costs + [s.fixed_order_cost for s in suppliers],
                dtype=float
            )
            integrality = np.ones(2 * n, dtype=int)

            # Upper bounds per supplier
            upper_caps = []
            for s in suppliers:
                cap_units = int(math.floor(cap_ratio * total_demand_qty))
                eff_upper = min(s.max_capacity, max(cap_units, s.moq if n == 1 else cap_units))
                upper_caps.append(max(0, eff_upper))

            lb = np.zeros(2 * n, dtype=float)
            ub = np.array(upper_caps + [1] * n, dtype=float)
            bounds = Bounds(lb, ub)

            A_rows = []
            b_l = []
            b_u = []

            # Constraint 1: Total units >= total_demand_qty (and <= 1.15 * total_demand_qty to prevent overbuy)
            demand_row = np.zeros(2 * n)
            demand_row[:n] = 1.0
            A_rows.append(demand_row)
            b_l.append(float(total_demand_qty))
            b_u.append(float(max(total_demand_qty, int(math.ceil(total_demand_qty * 1.15)))))

            # Constraint 2 & 3: For each supplier i:
            #   x_i - U_i * y_i <= 0   (cannot order unless y_i = 1)
            #   x_i - MOQ_i * y_i >= 0 (if y_i = 1, must order at least MOQ_i)
            for i, s in enumerate(suppliers):
                ub_row = np.zeros(2 * n)
                ub_row[i] = 1.0
                ub_row[n + i] = -float(upper_caps[i])
                A_rows.append(ub_row)
                b_l.append(-np.inf)
                b_u.append(0.0)

                if enforce_moq and s.moq > 0 and s.moq <= upper_caps[i]:
                    moq_row = np.zeros(2 * n)
                    moq_row[i] = 1.0
                    moq_row[n + i] = -float(s.moq)
                    A_rows.append(moq_row)
                    b_l.append(0.0)
                    b_u.append(np.inf)

            constraints = LinearConstraint(np.vstack(A_rows), b_l, b_u)
            return milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)

        res = _run_milp(share_cap, enforce_moq=True)

        # Fallback relaxation if strict MOQ + cap was infeasible
        if not res.success:
            solver_notes.append(
                "Strict concentration cap with MOQ bounds was infeasible; relaxed share cap to 100%."
            )
            res = _run_milp(1.0, enforce_moq=True)

        if not res.success:
            solver_notes.append("Relaxed MOQ floor due to small batch demand size.")
            res = _run_milp(1.0, enforce_moq=False)

        solve_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        if not res.success or res.x is None:
            raise RuntimeError(f"MILP solver failed to find a feasible allocation: {res.message}")

        x_sol = np.round(res.x[:n]).astype(int)
        y_sol = np.round(res.x[n:]).astype(int)
        total_allocated = int(np.sum(x_sol))

        allocations: List[Dict[str, Any]] = []
        total_direct_cost = 0.0
        total_risk_adjusted_cost = 0.0
        weighted_lead_time = 0.0
        weighted_reliability = 0.0
        weighted_disruption_risk = 0.0

        for i, s in enumerate(suppliers):
            qty = int(x_sol[i])
            if qty <= 0:
                continue
            share = (qty / total_allocated) if total_allocated > 0 else 0.0
            direct_cost = qty * s.effective_unit_cost + (s.fixed_order_cost if y_sol[i] else 0.0)
            risk_cost = qty * unit_obj_costs[i] + (s.fixed_order_cost if y_sol[i] else 0.0)

            total_direct_cost += direct_cost
            total_risk_adjusted_cost += risk_cost
            weighted_lead_time += share * s.lead_time_days
            weighted_reliability += share * s.reliability_score
            weighted_disruption_risk += share * s.disruption_risk_score

            allocations.append({
                "supplier_id": s.supplier_id,
                "supplier_code": s.supplier_code,
                "supplier_name": s.supplier_name,
                "country": s.country,
                "allocated_units": qty,
                "allocation_share_pct": round(share * 100.0, 1),
                "base_unit_cost": round(s.unit_cost, 2),
                "surcharge_pct": round(s.surcharge_pct, 1),
                "effective_unit_cost": round(s.effective_unit_cost, 2),
                "direct_procurement_cost": round(direct_cost, 2),
                "risk_adjusted_cost": round(risk_cost, 2),
                "lead_time_days": s.lead_time_days,
                "reliability_score": round(s.reliability_score * 100.0, 1),
                "disruption_risk_score": round(s.disruption_risk_score, 1),
                "moq": s.moq,
            })

        allocations.sort(key=lambda a: a["allocated_units"], reverse=True)

        # Baseline comparison: Naive single-source order to lowest base unit-cost supplier (typical ERP behavior)
        naive_idx = int(np.argmin([s.unit_cost for s in suppliers]))
        naive_sup = suppliers[naive_idx]
        naive_direct_cost = total_demand_qty * naive_sup.effective_unit_cost + naive_sup.fixed_order_cost
        naive_risk_cost = total_demand_qty * unit_obj_costs[naive_idx] + naive_sup.fixed_order_cost
        naive_disruption = naive_sup.disruption_risk_score

        expected_risk_savings = max(0.0, naive_risk_cost - total_risk_adjusted_cost)
        risk_reduction_pct = (
            max(0.0, ((naive_disruption - weighted_disruption_risk) / naive_disruption) * 100.0)
            if naive_disruption > 0
            else 0.0
        )

        return {
            "sku": sku,
            "requested_quantity": total_demand_qty,
            "total_allocated_quantity": total_allocated,
            "solver_engine": "SciPy HiGHS Mixed-Integer Linear Programming (MILP)",
            "solver_status": "OPTIMAL",
            "solve_time_ms": solve_time_ms,
            "parameters": {
                "risk_aversion_lambda": risk_aversion_lambda,
                "max_single_supplier_share_pct": round(share_cap * 100.0, 1),
                "target_lead_time_days": target_lead_time_days,
            },
            "summary": {
                "total_direct_cost": round(total_direct_cost, 2),
                "total_risk_adjusted_cost": round(total_risk_adjusted_cost, 2),
                "naive_single_source_supplier": naive_sup.supplier_name,
                "naive_direct_cost": round(naive_direct_cost, 2),
                "naive_risk_adjusted_cost": round(naive_risk_cost, 2),
                "expected_risk_cost_savings": round(expected_risk_savings, 2),
                "disruption_risk_reduction_pct": round(risk_reduction_pct, 1),
                "weighted_lead_time_days": round(weighted_lead_time, 1),
                "weighted_reliability_pct": round(weighted_reliability * 100.0, 1),
                "weighted_disruption_risk": round(weighted_disruption_risk, 1),
                "active_suppliers_count": len(allocations),
            },
            "allocations": allocations,
            "solver_notes": solver_notes,
        }


milp_optimizer = MultiSupplierMILPOptimizer()
