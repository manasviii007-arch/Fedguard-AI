# FedGuard AI - API Design

## API Standards
- **Protocol:** RESTful APIs over HTTPS
- **Authentication:** OAuth 2.0 with JWT tokens
- **Content Type:** JSON (application/json)
- **Versioning:** URL-based (/api/v1/)
- **Rate Limiting:** Per-endpoint and per-user limits
- **Pagination:** Cursor-based for large datasets
- **Error Handling:** Standardized error response format

## Base URL Structure
```
https://api.fedguard.ai/v1/{service}/{resource}
```

## Authentication & Authorization

### Authentication Endpoints

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "mfa_code": "123456" // Optional, for MFA-enabled accounts
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "DCA_AGENT",
    "permissions": ["cases:read", "cases:write"]
  }
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

## Case Management APIs

### Case Lifecycle APIs

#### Create Case
```http
POST /api/v1/cases
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "customer_id": "uuid",
  "principal_amount": 50000.00,
  "outstanding_amount": 55000.00,
  "overdue_amount": 5000.00,
  "overdue_days": 45,
  "product_type": "PERSONAL_LOAN",
  "account_number": "ACC123456789",
  "original_due_date": "2024-01-01",
  "interest_rate": 12.5,
  "penalty_amount": 500.00,
  "tags": ["priority", "high-value"],
  "custom_fields": {
    "loan_purpose": "medical_emergency",
    "employment_sector": "IT"
  }
}

Response:
{
  "id": "uuid",
  "case_number": "CASE-2024-000001",
  "status": "new",
  "risk_score": 75.5,
  "recovery_probability": 65.2,
  "created_at": "2024-01-09T10:00:00Z",
  "_links": {
    "self": "/api/v1/cases/uuid",
    "customer": "/api/v1/customers/uuid",
    "payments": "/api/v1/cases/uuid/payments"
  }
}
```

#### Get Case Details
```http
GET /api/v1/cases/{case_id}
Authorization: Bearer {access_token}

Response:
{
  "id": "uuid",
  "case_number": "CASE-2024-000001",
  "customer": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919876543210"
  },
  "debt_details": {
    "principal_amount": 50000.00,
    "outstanding_amount": 55000.00,
    "overdue_amount": 5000.00,
    "overdue_days": 45,
    "interest_rate": 12.5
  },
  "status": "assigned",
  "assigned_agent": {
    "id": "uuid",
    "name": "Agent Smith",
    "email": "smith@dca.com"
  },
  "ai_insights": {
    "risk_score": 75.5,
    "recovery_probability": 65.2,
    "key_factors": ["payment_history", "employment_stability"],
    "recommended_action": "personal_visit"
  },
  "timeline": {
    "created_at": "2024-01-09T10:00:00Z",
    "assigned_at": "2024-01-09T11:30:00Z",
    "next_action_date": "2024-01-16T00:00:00Z"
  },
  "communications": {
    "total_count": 5,
    "last_communication": "2024-01-08T15:30:00Z"
  }
}
```

#### Update Case
```http
PUT /api/v1/cases/{case_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "in_progress",
  "assigned_agent_id": "uuid",
  "notes": "Customer agreed to payment plan",
  "next_action_date": "2024-01-16",
  "custom_fields": {
    "customer_response": "agreed_to_plan"
  }
}
```

#### Assign Case to DCA
```http
POST /api/v1/cases/{case_id}/assign
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "dca_id": "uuid",
  "assigned_agent_id": "uuid",
  "assignment_type": "PERMANENT",
  "reason": "High priority case requiring specialized handling",
  "sla_days": 30
}

Response:
{
  "assignment_id": "uuid",
  "case_id": "case_uuid",
  "dca": {
    "id": "uuid",
    "name": "Professional Recovery Services",
    "contact_email": "assignments@prs.com"
  },
  "assigned_agent": {
    "id": "uuid",
    "name": "Senior Agent Johnson"
  },
  "assigned_at": "2024-01-09T14:30:00Z",
  "sla_deadline": "2024-02-08T23:59:59Z",
  "status": "active"
}
```

#### Escalate Case
```http
POST /api/v1/cases/{case_id}/escalate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "escalation_type": "LEGAL_REVIEW",
  "reason": "Customer non-responsive after multiple attempts",
  "current_status": "Customer not responding to calls or messages",
  "requested_action": "Legal notice preparation",
  "priority": "high"
}
```

#### Close Case
```http
POST /api/v1/cases/{case_id}/close
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "closure_type": "FULL_SETTLEMENT",
  "final_amount": 55000.00,
  "settlement_date": "2024-01-09",
  "closure_reason": "Customer paid full outstanding amount",
  "notes": "Case successfully resolved through payment plan"
}
```

### Case Search & Filtering

#### Search Cases
```http
GET /api/v1/cases?status=assigned&priority=high&overdue_days_min=30&dca_id=uuid&page=1&limit=20
Authorization: Bearer {access_token}

Response:
{
  "data": [
    {
      "id": "uuid",
      "case_number": "CASE-2024-000001",
      "customer_name": "John Doe",
      "outstanding_amount": 55000.00,
      "overdue_days": 45,
      "status": "assigned",
      "priority": "high",
      "assigned_agent": "Agent Smith",
      "risk_score": 75.5,
      "next_action_date": "2024-01-16"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "total_pages": 8
  },
  "filters": {
    "status": "assigned",
    "priority": "high",
    "overdue_days_min": 30
  }
}
```

#### Bulk Case Operations
```http
POST /api/v1/cases/bulk
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "operation": "assign",
  "case_ids": ["uuid1", "uuid2", "uuid3"],
  "parameters": {
    "dca_id": "uuid",
    "assigned_agent_id": "uuid",
    "reason": "Bulk assignment for high-priority cases"
  }
}

Response:
{
  "operation_id": "uuid",
  "total_cases": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "case_id": "uuid1",
      "status": "success",
      "message": "Case assigned successfully"
    }
  ]
}
```

## Payment Management APIs

### Payment Processing

#### Record Payment
```http
POST /api/v1/payments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "case_id": "uuid",
  "amount": 10000.00,
  "payment_method": "ONLINE",
  "payment_date": "2024-01-09",
  "settlement_type": "partial",
  "gateway_name": "Razorpay",
  "gateway_transaction_id": "pay_123456789",
  "notes": "First installment of payment plan"
}

Response:
{
  "payment_id": "uuid",
  "payment_reference": "PAY-2024-000001",
  "status": "confirmed",
  "confirmed_at": "2024-01-09T15:30:00Z",
  "case_update": {
    "previous_outstanding": 55000.00,
    "new_outstanding": 45000.00,
    "status": "in_progress"
  }
}
```

#### Create Settlement Plan
```http
POST /api/v1/cases/{case_id}/settlement-plans
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "plan_type": "EMI",
  "total_amount": 55000.00,
  "installment_count": 6,
  "interest_rate": 0,
  "processing_fee": 500.00,
  "first_installment_date": "2024-02-01",
  "last_installment_date": "2024-07-01",
  "terms_conditions": "Customer agrees to pay monthly installments..."
}
```

## Communication APIs

### Send Communication
```http
POST /api/v1/communications
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "case_id": "uuid",
  "channel": "SMS",
  "message_type": "PAYMENT_REMINDER",
  "template_id": "uuid",
  "personalization": {
    "customer_name": "John Doe",
    "outstanding_amount": "₹45,000",
    "due_date": "2024-01-15"
  },
  "scheduled_at": "2024-01-10T09:00:00Z" // Optional
}

Response:
{
  "communication_id": "uuid",
  "status": "scheduled",
  "estimated_delivery": "2024-01-10T09:05:00Z",
  "content_preview": "Dear John Doe, your outstanding amount of ₹45,000 is due on 2024-01-15..."
}
```

#### Get Communication Templates
```http
GET /api/v1/communications/templates?channel=SMS&message_type=REMINDER
Authorization: Bearer {access_token}

Response:
{
  "templates": [
    {
      "id": "uuid",
      "name": "Payment Reminder SMS",
      "channel": "SMS",
      "message_type": "REMINDER",
      "subject": "",
      "body": "Dear {customer_name}, your payment of {outstanding_amount} is due on {due_date}. Please contact us.",
      "variables": ["customer_name", "outstanding_amount", "due_date"],
      "is_active": true
    }
  ]
}
```

## AI/ML APIs

### Risk Assessment

#### Get AI Risk Score
```http
GET /api/v1/ai/risk-assessment/{case_id}
Authorization: Bearer {access_token}

Response:
{
  "case_id": "uuid",
  "current_assessment": {
    "risk_score": 75.5,
    "recovery_probability": 65.2,
    "priority_score": 82.1,
    "confidence_level": 92.0,
    "key_factors": [
      {
        "factor": "payment_history",
        "impact": "negative",
        "weight": 0.35,
        "description": "Multiple missed payments in last 6 months"
      },
      {
        "factor": "employment_stability",
        "impact": "positive", 
        "weight": 0.25,
        "description": "Stable employment for 3+ years"
      }
    ],
    "recommended_strategy": "personal_visit",
    "explanation": "Based on behavioral patterns and financial indicators..."
  },
  "model_info": {
    "model_version": "v2.3.1",
    "model_type": "ensemble",
    "assessed_at": "2024-01-09T14:00:00Z"
  }
}
```

#### Batch Risk Assessment
```http
POST /api/v1/ai/risk-assessment/batch
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "case_ids": ["uuid1", "uuid2", "uuid3"],
  "include_explanation": true
}

Response:
{
  "batch_id": "uuid",
  "total_cases": 3,
  "assessments": [
    {
      "case_id": "uuid1",
      "risk_score": 75.5,
      "recovery_probability": 65.2,
      "priority_score": 82.1,
      "processing_time_ms": 250
    }
  ],
  "completed_at": "2024-01-09T14:02:30Z"
}
```

## Analytics & Reporting APIs

### Dashboard APIs

#### Get Dashboard Summary
```http
GET /api/v1/analytics/dashboard-summary?organization_id=uuid&period=30d
Authorization: Bearer {access_token}

Response:
{
  "period": "30d",
  "organization_id": "uuid",
  "summary": {
    "total_cases": 1250,
    "active_cases": 850,
    "closed_cases": 400,
    "recovery_rate": 68.5,
    "total_recovered": 12500000.00,
    "avg_collection_time_days": 45,
    "sla_compliance_rate": 94.2
  },
  "trends": {
    "case_volume": {
      "current": 1250,
      "previous": 1180,
      "change": 5.9
    },
    "recovery_rate": {
      "current": 68.5,
      "previous": 65.2,
      "change": 3.3
    }
  },
  "top_performers": [
    {
      "dca_id": "uuid",
      "name": "Professional Recovery Services",
      "recovery_rate": 78.5,
      "cases_handled": 150
    }
  ]
}
```

#### Get DCA Performance Report
```http
GET /api/v1/analytics/dca-performance?dca_id=uuid&period=90d
Authorization: Bearer {access_token}

Response:
{
  "dca_id": "uuid",
  "period": "90d",
  "performance_metrics": {
    "total_cases_assigned": 450,
    "cases_resolved": 320,
    "recovery_rate": 71.1,
    "avg_resolution_time_days": 38,
    "sla_breaches": 12,
    "customer_satisfaction": 4.2,
    "compliance_score": 96.8
  },
  "case_distribution": {
    "by_status": {
      "new": 50,
      "in_progress": 180,
      "resolved": 320
    },
    "by_priority": {
      "high": 120,
      "medium": 200,
      "low": 130
    }
  },
  "trend_analysis": {
    "recovery_rate_trend": [
      {"month": "2023-11", "rate": 68.5},
      {"month": "2023-12", "rate": 70.2},
      {"month": "2024-01", "rate": 71.1}
    ]
  }
}
```

## Workflow & SLA APIs

### Workflow Management

#### Trigger Workflow Action
```http
POST /api/v1/workflows/trigger
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "case_id": "uuid",
  "action_type": "SEND_REMINDER",
  "parameters": {
    "reminder_type": "PAYMENT",
    "channel": "SMS",
    "days_overdue": 30
  }
}
```

#### Get SLA Status
```http
GET /api/v1/sla/cases/{case_id}/status
Authorization: Bearer {access_token}

Response:
{
  "case_id": "uuid",
  "sla_status": "AT_RISK",
  "sla_deadline": "2024-01-15T23:59:59Z",
  "days_remaining": 6,
  "breach_risk_level": "medium",
  "last_activity": "2024-01-03T10:30:00Z",
  "recommended_actions": [
    "Schedule follow-up call within 24 hours",
    "Send escalation email to DCA manager"
  ]
}
```

## Audit & Compliance APIs

### Audit Trail

#### Get Audit Logs
```http
GET /api/v1/audit/logs?entity_type=CASE&entity_id=uuid&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {access_token}

Response:
{
  "logs": [
    {
      "id": "uuid",
      "event_type": "CASE_STATUS_CHANGED",
      "event_category": "BUSINESS",
      "entity_type": "CASE",
      "entity_id": "uuid",
      "user_id": "uuid",
      "user_name": "Agent Smith",
      "action": "Changed status from NEW to ASSIGNED",
      "previous_values": {"status": "new"},
      "new_values": {"status": "assigned", "assigned_agent_id": "uuid"},
      "occurred_at": "2024-01-09T11:30:00Z",
      "ip_address": "192.168.1.100"
    }
  ],
  "pagination": {
    "total": 25,
    "page": 1,
    "limit": 50
  }
}
```

#### Generate Compliance Report
```http
POST /api/v1/compliance/reports
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "report_type": "RBI_MONTHLY",
  "organization_id": "uuid",
  "report_period_start": "2024-01-01",
  "report_period_end": "2024-01-31",
  "include_analytics": true
}

Response:
{
  "report_id": "uuid",
  "status": "generating",
  "estimated_completion": "2024-01-09T16:00:00Z",
  "report_details": {
    "type": "RBI_MONTHLY",
    "period": "January 2024",
    "organization": "ABC Bank Ltd."
  }
}
```

## Error Response Format

### Standard Error Response
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "principal_amount",
        "message": "Amount must be greater than 0",
        "value": -1000
      }
    ],
    "request_id": "req_123456789",
    "timestamp": "2024-01-09T14:30:00Z"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_FAILED`: Invalid credentials
- `AUTHORIZATION_FAILED`: Insufficient permissions
- `VALIDATION_ERROR`: Request validation failed
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: API rate limit exceeded
- `SERVICE_UNAVAILABLE`: Service temporarily unavailable
- `CONFLICT`: Resource conflict (duplicate, etc.)

## API Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641734400
X-RateLimit-Window: 3600
```

### Rate Limit Tiers
- **Tier 1 (Basic):** 100 requests/minute, 1000 requests/hour
- **Tier 2 (Standard):** 500 requests/minute, 5000 requests/hour
- **Tier 3 (Premium):** 1000 requests/minute, 10000 requests/hour

## Webhook Events

### Webhook Payload Structure
```json
{
  "event_id": "evt_123456789",
  "event_type": "CASE_STATUS_CHANGED",
  "event_timestamp": "2024-01-09T14:30:00Z",
  "data": {
    "case_id": "uuid",
    "previous_status": "new",
    "new_status": "assigned",
    "assigned_agent_id": "uuid"
  },
  "metadata": {
    "organization_id": "uuid",
    "user_id": "uuid"
  }
}
```

### Supported Webhook Events
- `CASE_CREATED`: New case created
- `CASE_STATUS_CHANGED`: Case status updated
- `CASE_ASSIGNED`: Case assigned to agent/DCA
- `PAYMENT_RECEIVED`: Payment recorded
- `COMMUNICATION_SENT`: Communication dispatched
- `SLA_BREACH_DETECTED`: SLA violation identified
- `ESCALATION_TRIGGERED`: Case escalated
- `COMPLIANCE_VIOLATION`: Compliance issue detected