# Agent-to-Agent (A2A) ERP Domain Specification

This document specifies the message protocol and schema for Agent-to-Agent (A2A) interactions in the Enterprise Resource Planning (ERP) domain on AgentMesh.

---

## 1. Message Encapsulation

All A2A messages follow the standardized `AgentMessage` envelope schema over Nostr Kind `29001`:

```json
{
  "id": "msg_01J6XYZ...",
  "sender": "npub1sender...",
  "receiver": "npub1erpseedagent...",
  "type": "task",
  "payload": {
    "action": "<domain_action>",
    "params": { ... }
  },
  "timestamp": 1725280000.0
}
```

Responses are returned with `type: "response"`:

```json
{
  "id": "msg_01J6XYZ_RESP",
  "sender": "npub1erpseedagent...",
  "receiver": "npub1sender...",
  "type": "response",
  "payload": {
    "status": "success",
    "action": "<domain_action>",
    "tenant_id": 1,
    "result": { ... }
  },
  "timestamp": 1725280005.0
}
```

---

## 2. Action Capabilities by Module

### 2.1 Sales (`sales`)
- `sales.create_order`: Create sales order.
  - Params: `customer_id` (int), `items` (list of item dicts).
- `sales.list_orders`: Retrieve sales orders.
- `sales.create_invoice`: Create customer invoice.

### 2.2 Purchases (`purchases`)
- `purchases.create_order`: Create purchase order to supplier.
  - Params: `supplier_id` (int), `items` (list).
- `purchases.list_orders`: Retrieve purchase orders.

### 2.3 Inventory (`inventory`)
- `inventory.move_stock`: Move product quantity between locations.
  - Params: `product_id` (int), `quantity` (float), `source_location` (str), `target_location` (str).
- `inventory.check_stock`: Query stock level for product.

### 2.4 Accounting (`accounting`)
- `accounting.prima_nota`: Register general ledger entry.
  - Params: `date` (str), `entries` (list).
- `accounting.liquidazione_iva`: Run VAT liquidation calculation.

### 2.5 Fattura Elettronica (`fattura_elettronica`)
- `fattura_elettronica.generate_xml`: Generate Italian FatturaPA 1.2 XML and store in IPFS Vault.
  - Params: `invoice_number` (str), `invoice_date` (str), `supplier` (dict), `customer` (dict), `lines` (list).
  - Response: `{ "status": "generated", "invoice_number": "...", "ipfs_cid": "Qm...", "ipfs_url": "https://ipfs.io/ipfs/Qm...", "xml_content": "..." }`

### 2.6 Low-Code AI Builder (`builder`)
- `builder.generate_model`: Synthesize SysModel schema from text prompt.
  - Params: `description` (str), `model_name` (optional str).
- `builder.generate_view`: Synthesize UI form/list layout.
  - Params: `model_name` (str), `view_type` (str: `list`, `form`, `kanban`).
- `builder.generate_workflow`: Synthesize workflow rule.
  - Params: `workflow_name` (str), `description` (str).

### 2.7 Dynamic Model CRUD (`data.<model>.<op>`)
- `data.<model>.list`: List records for SysModel.
- `data.<model>.create`: Create new record for SysModel.
- `data.<model>.get`: Get single record by ID.
- `data.<model>.update`: Update record.
- `data.<model>.delete`: Delete record.
