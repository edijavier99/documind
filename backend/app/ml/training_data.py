"""
Datos de entrenamiento sintéticos para el clasificador de documentos.
En producción reemplazarías esto con documentos reales etiquetados.
"""

TRAINING_DATA = [
    # ── CONTRACTS ─────────────────────────────────────────────────
    ("This agreement is entered into between the parties herein. The terms and conditions set forth obligations for both parties. This contract shall be governed by applicable law.", "contract"),
    ("Service agreement between client and provider. Payment terms are net 30 days. Either party may terminate this agreement with 30 days written notice.", "contract"),
    ("Employment contract for the position of Software Engineer. The employee agrees to maintain confidentiality. Non-disclosure agreement is part of this contract.", "contract"),
    ("Lease agreement for commercial property. Monthly rent payments due on the first of each month. Security deposit required upon signing.", "contract"),
    ("Partnership agreement establishing rights and responsibilities. Profit sharing shall be divided equally. Disputes resolved through arbitration.", "contract"),
    ("Software license agreement grants limited non-exclusive rights. Licensee may not sublicense or transfer rights. All intellectual property remains with licensor.", "contract"),
    ("Consulting agreement for professional services. Consultant shall invoice monthly. Confidentiality clause applies to all proprietary information.", "contract"),
    ("Acuerdo de servicios entre las partes contratantes. Las obligaciones y términos quedan establecidos en las siguientes cláusulas del contrato.", "contract"),
    ("Vendor agreement for supply of goods. Delivery terms FOB destination. Warranty period of 12 months from date of delivery.", "contract"),
    ("Non-compete agreement restricts employee from working with competitors. Duration of restriction is 24 months post-employment.", "contract"),

    # ── INVOICES ──────────────────────────────────────────────────
    ("Invoice #2024-001. Bill to: Acme Corp. Amount due: $5,000. Payment due date: 30 days. VAT included at 20%.", "invoice"),
    ("Tax invoice for professional services rendered. Subtotal: $2,500. Tax: $250. Total amount due: $2,750.", "invoice"),
    ("Purchase order invoice. Item description: Software licenses x10. Unit price: $99. Total: $990. Please remit payment.", "invoice"),
    ("Factura numero 456. Cliente: Empresa XYZ. Importe total: 3.500 euros. IVA 21% incluido. Fecha de vencimiento: 30 dias.", "invoice"),
    ("Proforma invoice for import customs. Goods description: Electronic components. FOB value: $15,000. Country of origin: USA.", "invoice"),
    ("Credit note issued against invoice #789. Reason: returned goods. Credit amount: $500. Apply against next invoice.", "invoice"),
    ("Monthly retainer invoice for legal services. Hours billed: 20. Rate: $300/hour. Total: $6,000. Wire transfer preferred.", "invoice"),
    ("Utility bill for electricity consumption. Units consumed: 1,500 kWh. Rate per unit: $0.12. Total due: $180.", "invoice"),
    ("Subscription renewal invoice. Annual plan: $1,200. Discount applied: 10%. Amount charged to card on file: $1,080.", "invoice"),
    ("Invoice for construction services. Labour: $8,000. Materials: $12,000. Overhead: $2,000. Project total: $22,000.", "invoice"),

    # ── REPORTS ───────────────────────────────────────────────────
    ("Executive summary of Q3 financial results. Revenue increased 15% year over year. Key findings indicate strong market position.", "report"),
    ("Annual report 2024. Business performance analysis. Market share grew to 23%. Recommendations for strategic investment included.", "report"),
    ("Research report on consumer behavior trends. Methodology: survey of 1,000 participants. Findings suggest shift to digital channels.", "report"),
    ("Informe de ventas trimestral. Analisis de resultados. Las conclusiones muestran crecimiento sostenido en el mercado objetivo.", "report"),
    ("Audit report findings and recommendations. Internal controls assessment. Risk areas identified: three high, five medium priority.", "report"),
    ("Market analysis report. Competitive landscape overview. Summary of industry trends and growth opportunities identified.", "report"),
    ("Project status report. Milestones achieved this quarter. Budget utilization at 78%. Timeline on track for delivery.", "report"),
    ("Environmental impact assessment report. Study findings indicate minimal disruption. Recommended mitigation measures outlined.", "report"),
    ("Sales performance report. Top performers by region. Analysis of conversion rates and pipeline health indicators.", "report"),
    ("Due diligence report for acquisition target. Financial analysis summary. Risk assessment and valuation conclusions.", "report"),

    # ── TECHNICAL ─────────────────────────────────────────────────
    ("API documentation for REST endpoints. Authentication using JWT tokens. Rate limiting: 1000 requests per hour.", "technical"),
    ("System architecture overview. Microservices deployed on Kubernetes. Database layer uses PostgreSQL with read replicas.", "technical"),
    ("README for open source library. Installation: pip install package. Configuration requires environment variables.", "technical"),
    ("Technical specification for mobile application. Frontend React Native. Backend Node.js with GraphQL API.", "technical"),
    ("Infrastructure as code documentation. Terraform modules for AWS deployment. ECS cluster with auto-scaling enabled.", "technical"),
    ("Database schema documentation. Entity relationship diagram. Indexes optimized for query performance.", "technical"),
    ("DevOps runbook for incident response. Deployment pipeline using GitHub Actions. Rollback procedure documented.", "technical"),
    ("Machine learning model documentation. Training data: 50,000 samples. Model accuracy: 94%. Inference latency: 50ms.", "technical"),
    ("Security vulnerability assessment. CVE analysis of dependencies. Penetration testing results and remediation steps.", "technical"),
    ("Code review guidelines and standards. Pull request process. Unit test coverage requirement minimum 80 percent.", "technical"),
]
