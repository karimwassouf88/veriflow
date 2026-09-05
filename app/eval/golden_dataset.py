INVOICE_GOLDEN_SET = [
    {
        "id": "acme_clean",
        "raw_text": """ACME LOGISTICS INC.
100 Supply Chain Way, Suite 400
Chicago, IL 60601
Tax ID: US-987654321
INVOICE
Invoice Number INV-2026-08912 Invoice Date August 25, 2026
Due Date September 24, 2026 Purchase Order Ref PO-88341
BILL TO:
VeriFlow Enterprise Systems
742 Evergreen Terrace
Springfield, OR 97477
ITEM DESCRIPTION QTY UNIT PRICE ($) TOTAL AMOUNT ($)
Dell UltraSharp 27" Monitor 10 450.00 4,500.00
Ergonomic Office Chair 15 250.00 3,750.00
USB-C Docking Station 10 180.00 1,800.00
Cat6 Ethernet Cable (10m) 25 12.00 300.00
SUBTOTAL: $10,350.00
TAX (8%): $828.00
SHIPPING & HANDLING: $150.00
TOTAL AMOUNT DUE: $11,328.00
PAYMENT TERMS:
Net 30 Days. Please remit payment via ACH transfer.""",
        "expected": {
            "vendor_name": "ACME LOGISTICS INC.", "invoice_number": "INV-2026-08912",
            "invoice_date": "2026-08-25", "due_date": "2026-09-24",
            "total_amount": 11328.00, "currency": "USD", "po_reference": "PO-88341",
        },
    },
    {
        "id": "mikes_hardware_messy",
        "raw_text": """MIKE'S HARDWARE & SUPPLY
12 King St
Phone: 555-0199
Ref#: 4471-B
Date: 9/8/26
Terms: 2/10 net 30
Bal Due: see below
Sold To: VeriFlow c/o clerk
Qty Item Price Amt
8 3/4" Copper Pipe (10ft) 22.50 180.00
3 Pipe Fitting Kit 15.00 12.00 36.00
1 Shop Labor (4 hrs) 45.00 180.00
2 Misc Hardware 8.75 17.50
Subtotal: 413.50
Misc Fee: 15.00
** +45 rush - ask John **
Amount:  458.50
(pd 200 dep, bal 258.50??)
Make checks payable to M. Torres. No returns after 30 days.""",
        # invoice_date deliberately omitted — "9/8/26" has no single correct reading
        "expected": {
            "vendor_name": "MIKE'S HARDWARE & SUPPLY", "invoice_number": "4471-B",
            "due_date": None, "total_amount": 458.50, "currency": None, "po_reference": None,
        },
    },
    {
        "id": "nimbus_clean",
        "raw_text": """NIMBUS CLOUD HARDWARE LTD.
400 Datacenter Drive, Suite 12
Austin, TX 78701
Tax ID: US-445566778
INVOICE
Invoice Number  INV-7734
Invoice Date  August 20, 2026
Due Date  September 19, 2026
Purchase Order Ref  PO-7734-A
BILL TO:
VeriFlow Enterprise Systems
742 Evergreen Terrace, Springfield, OR 97477
ITEM QTY UNIT PRICE ($) TOTAL ($)
Server Rack Unit 2 1200.00 2400.00
Network Switch 24-port 3 350.00 1050.00
Rack Mount Kit 4 50.00 200.00
Installation Labor (hrs) 8 100.00 800.00
SUBTOTAL: 4,450.00
TAX (8%): 356.00
SHIPPING & HANDLING: 150.00
TOTAL AMOUNT DUE: 4,956.00
PAYMENT TERMS:
Net 30 Days. Remit payment via ACH transfer.""",
        "expected": {
            "vendor_name": "NIMBUS CLOUD HARDWARE LTD.", "invoice_number": "INV-7734",
            "invoice_date": "2026-08-20", "due_date": "2026-09-19",
            "total_amount": 4956.00, "currency": "USD", "po_reference": "PO-7734-A",
        },
    },
]