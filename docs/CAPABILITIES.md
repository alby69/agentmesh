# AgentMesh Capabilities Registry

This document lists capability sets exposed across AgentMesh workspace applications.

---

## `erpseed-agent` Capabilities Matrix

| Agent / Module | Capability Name | Description |
|---|---|---|
| **SalesAgent** | `erp.sales.create_order` | Create sales order for customer |
| **SalesAgent** | `erp.sales.list_orders` | List sales orders |
| **SalesAgent** | `erp.sales.create_invoice` | Generate customer invoice |
| **PurchaseAgent** | `erp.purchases.create_order` | Create purchase order for vendor |
| **PurchaseAgent** | `erp.purchases.list_orders` | List supplier purchase orders |
| **InventoryAgent** | `erp.inventory.move_stock` | Move stock quantity between warehouse locations |
| **InventoryAgent** | `erp.inventory.check_stock` | Query inventory stock levels |
| **InventoryAgent** | `erp.inventory.track_lot` | Track lot and serial numbers |
| **AccountingAgent** | `erp.accounting.prima_nota` | Register general ledger entry (Prima Nota) |
| **AccountingAgent** | `erp.accounting.liquidazione_iva` | Calculate periodic VAT liquidation |
| **HRAgent** | `erp.hr.employee_list` | List employees |
| **HRAgent** | `erp.hr.log_attendance` | Record daily attendance status |
| **HRAgent** | `erp.hr.get_payroll` | Get payroll summary |
| **ManufacturingAgent** | `erp.manufacturing.get_bom` | Retrieve Bill of Materials (BOM) |
| **ManufacturingAgent** | `erp.manufacturing.create_odp` | Create Production Order (ODP) |
| **ManufacturingAgent** | `erp.manufacturing.run_mrp` | Run Material Requirements Planning (MRP) |
| **CRMAgent** | `erp.crm.create_lead` | Create new sales lead |
| **CRMAgent** | `erp.crm.list_opportunities` | List pipeline opportunities |
| **FEAgent** | `erp.fattura_elettronica.generate_xml` | Generate FatturaPA 1.2 XML & store on IPFS Vault |
| **FEAgent** | `erp.fattura_elettronica.send_sdi` | Submit XML invoice to SDI gateway |
| **WorkflowAgent** | `erp.workflow.create_automation` | Create automated rule trigger |
| **WorkflowAgent** | `erp.webhook.register` | Register webhook event handler |
| **AIBuilderAgent** | `erp.builder.generate_model` | Synthesize SysModel schema from natural language |
| **AIBuilderAgent** | `erp.builder.generate_view` | Synthesize UI layout (form, list, kanban) |
| **AIBuilderAgent** | `erp.builder.generate_workflow` | Synthesize trigger-action workflow rule |
| **Dynamic API** | `data.<model>.list` | List records for dynamic low-code SysModel |
| **Dynamic API** | `data.<model>.create` | Create record for dynamic low-code SysModel |
| **Dynamic API** | `data.<model>.get` | Get single record for dynamic low-code SysModel |
| **Dynamic API** | `data.<model>.update` | Update record for dynamic low-code SysModel |
| **Dynamic API** | `data.<model>.delete` | Delete record for dynamic low-code SysModel |
