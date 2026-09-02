"""Human Resources module agent for employee records, attendance, and payroll."""

from __future__ import annotations

from typing import Dict, Any, Optional
from erpseed_agent.config import ERPSeedConfig
from erpseed_agent.agents.base_module_agent import ERPModuleAgent
from erpseed_agent.bridge.executor import ERPSeedBridge


class HRAgent(ERPModuleAgent):
    """Specialized agent for Human Resources operations."""

    def __init__(self, config: ERPSeedConfig, bridge: Optional[ERPSeedBridge] = None):
        super().__init__(
            config=config,
            module_name="hr",
            capabilities=[
                "erp.hr.employee_list",
                "erp.hr.log_attendance",
                "erp.hr.get_payroll",
                "hr.employee_list",
                "hr.log_attendance",
                "hr.get_payroll",
            ],
            bridge=bridge,
        )

    async def log_attendance(
        self, employee_id: int, date: str, status: str, tenant_id: int = 1, api_key: str = ""
    ) -> Dict[str, Any]:
        params = {"employee_id": employee_id, "date": date, "status": status}
        return await self.execute_module_action("hr.log_attendance", params, tenant_id=tenant_id, api_key=api_key)
