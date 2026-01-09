# FedGuard AI - Data Models

## Core Entity Models

### 1. User Management Models

#### User Entity
```sql
-- PostgreSQL Schema
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    mfa_enabled BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_status ON users(status);
```

#### Role Entity
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    hierarchy_level INTEGER NOT NULL DEFAULT 0,
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample Roles
INSERT INTO roles (name, description, permissions, hierarchy_level, is_system_role) VALUES
('SUPER_ADMIN', 'System administrator with full access', '{"*": ["read", "write", "delete", "admin"]}', 100, true),
('ENTERPRISE_ADMIN', 'Enterprise administrator', '{"cases": ["read", "write", "admin"], "users": ["read", "write", "admin"], "reports": ["read", "admin"]}', 90, true),
('DCA_MANAGER', 'DCA manager with team oversight', '{"cases": ["read", "write"], "team": ["read", "write"], "reports": ["read"]}', 70, true),
('DCA_AGENT', 'DCA collection agent', '{"cases": ["read", "write"], "communications": ["read", "write"]}', 50, true),
('CUSTOMER', 'Customer portal access', '{"profile": ["read", "write"], "cases": ["read"], "payments": ["read", "write"]}', 10, true);
```

#### Organization Entity
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('ENTERPRISE', 'DCA', 'REGULATOR')),
    registration_number VARCHAR(100),
    tax_id VARCHAR(50),
    address JSONB,
    contact_info JSONB,
    settings JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Case Management Models

#### Case Entity
```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID NOT NULL REFERENCES customers(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    dca_id UUID REFERENCES organizations(id), -- DCA organization
    assigned_agent_id UUID REFERENCES users(id),
    
    -- Debt Information
    principal_amount DECIMAL(15,2) NOT NULL,
    outstanding_amount DECIMAL(15,2) NOT NULL,
    overdue_amount DECIMAL(15,2) NOT NULL,
    overdue_days INTEGER NOT NULL DEFAULT 0,
    interest_rate DECIMAL(5,2),
    penalty_amount DECIMAL(15,2) DEFAULT 0,
    
    -- Case Details
    product_type VARCHAR(50) NOT NULL, -- LOAN, CREDIT_CARD, MORTGAGE, etc.
    account_number VARCHAR(100) NOT NULL,
    original_due_date DATE NOT NULL,
    case_priority VARCHAR(20) DEFAULT 'medium' CHECK (case_priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Status and Workflow
    status VARCHAR(50) NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'assigned', 'in_progress', 'escalated', 'legal', 'settled', 'closed')),
    sub_status VARCHAR(50),
    workflow_stage VARCHAR(100),
    
    -- AI Scoring
    risk_score DECIMAL(5,2) DEFAULT 0,
    recovery_probability DECIMAL(5,2) DEFAULT 0,
    ai_insights JSONB DEFAULT '{}',
    
    -- SLA and Timeline
    sla_breach_date TIMESTAMP,
    next_action_date DATE,
    escalation_level INTEGER DEFAULT 0,
    
    -- Metadata
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_cases_customer ON cases(customer_id);
CREATE INDEX idx_cases_organization ON cases(organization_id);
CREATE INDEX idx_cases_dca ON cases(dca_id);
CREATE INDEX idx_cases_agent ON cases(assigned_agent_id);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_priority ON cases(case_priority);
CREATE INDEX idx_cases_due_date ON cases(original_due_date);
CREATE INDEX idx_cases_risk_score ON cases(risk_score DESC);
```

#### Customer Entity
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id VARCHAR(100) UNIQUE NOT NULL, -- External system ID
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    date_of_birth DATE,
    
    -- Address Information
    permanent_address JSONB,
    current_address JSONB,
    
    -- Financial Profile
    income_bracket VARCHAR(50),
    employment_status VARCHAR(50),
    employer_name VARCHAR(255),
    credit_score INTEGER,
    
    -- Behavioral Signals
    communication_preference VARCHAR(20) DEFAULT 'email',
    response_history JSONB DEFAULT '{}',
    payment_behavior JSONB DEFAULT '{}',
    
    -- Compliance
    consent_status JSONB DEFAULT '{}',
    data_privacy_preferences JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blocked')),
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);
```

#### Case History Entity
```sql
CREATE TABLE case_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    action_type VARCHAR(100) NOT NULL,
    action_description TEXT,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_fields JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- User who performed the action
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

CREATE INDEX idx_case_history_case ON case_history(case_id);
CREATE INDEX idx_case_history_performed_at ON case_history(performed_at DESC);
```

### 3. Payment Models

#### Payment Entity
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_reference VARCHAR(100) UNIQUE NOT NULL,
    case_id UUID NOT NULL REFERENCES cases(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    
    -- Payment Details
    amount DECIMAL(15,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL, -- CASH, CHEQUE, ONLINE, UPI, etc.
    payment_date DATE NOT NULL,
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Settlement Information
    settlement_type VARCHAR(50) DEFAULT 'full', -- full, partial, emi
    principal_amount DECIMAL(15,2),
    interest_amount DECIMAL(15,2),
    penalty_amount DECIMAL(15,2),
    
    -- Payment Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'failed', 'reversed')),
    confirmation_date TIMESTAMP,
    failure_reason TEXT,
    
    -- Gateway Information
    gateway_name VARCHAR(100),
    gateway_transaction_id VARCHAR(255),
    gateway_response JSONB DEFAULT '{}',
    
    -- Compliance
    receipt_generated BOOLEAN DEFAULT false,
    receipt_number VARCHAR(100),
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_payments_case ON payments(case_id);
CREATE INDEX idx_payments_customer ON payments(customer_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_payments_status ON payments(status);
```

#### Settlement Plan Entity
```sql
CREATE TABLE settlement_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    plan_type VARCHAR(50) NOT NULL, -- EMI, BULLET, CUSTOM
    total_amount DECIMAL(15,2) NOT NULL,
    installment_count INTEGER NOT NULL,
    
    -- Terms
    interest_rate DECIMAL(5,2),
    processing_fee DECIMAL(15,2) DEFAULT 0,
    first_installment_date DATE NOT NULL,
    last_installment_date DATE NOT NULL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'proposed' CHECK (status IN ('proposed', 'approved', 'active', 'completed', 'cancelled')),
    approval_date TIMESTAMP,
    approved_by UUID REFERENCES users(id),
    
    -- Metadata
    terms_conditions TEXT,
    customer_acceptance BOOLEAN DEFAULT false,
    acceptance_date TIMESTAMP,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);
```

### 4. Communication Models

#### Communication Entity
```sql
CREATE TABLE communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    
    -- Communication Details
    channel VARCHAR(50) NOT NULL, -- SMS, EMAIL, WHATSAPP, CALL, LETTER
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('outbound', 'inbound')),
    message_type VARCHAR(100), -- REMINDER, FOLLOW_UP, LEGAL_NOTICE, etc.
    
    -- Content
    subject VARCHAR(500),
    content TEXT NOT NULL,
    template_id UUID REFERENCES communication_templates(id),
    
    -- Delivery Information
    sender_id UUID REFERENCES users(id),
    recipient_contact VARCHAR(255) NOT NULL,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    
    -- Status and Response
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')),
    delivery_status VARCHAR(100),
    failure_reason TEXT,
    
    -- Response Tracking
    response_received BOOLEAN DEFAULT false,
    response_content TEXT,
    responded_at TIMESTAMP,
    
    -- Compliance
    consent_verified BOOLEAN DEFAULT true,
    compliance_flags JSONB DEFAULT '{}',
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_communications_case ON communications(case_id);
CREATE INDEX idx_communications_customer ON communications(customer_id);
CREATE INDEX idx_communications_channel ON communications(channel);
CREATE INDEX idx_communications_sent_at ON communications(sent_at DESC);
```

#### Communication Template Entity
```sql
CREATE TABLE communication_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    message_type VARCHAR(100) NOT NULL,
    
    -- Template Content
    subject_template TEXT,
    body_template TEXT NOT NULL,
    variables JSONB DEFAULT '[]', -- Available template variables
    
    -- Configuration
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 1,
    
    -- Compliance
    requires_approval BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approval_date TIMESTAMP,
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);
```

### 5. AI/ML Models

#### AI Risk Assessment Entity
```sql
CREATE TABLE ai_risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    
    -- Scores
    risk_score DECIMAL(5,2) NOT NULL, -- 0-100
    recovery_probability DECIMAL(5,2) NOT NULL, -- 0-100
    priority_score DECIMAL(5,2) NOT NULL, -- 0-100
    
    -- Feature Inputs
    behavioral_signals JSONB DEFAULT '{}',
    financial_indicators JSONB DEFAULT '{}',
    demographic_factors JSONB DEFAULT '{}',
    historical_patterns JSONB DEFAULT '{}',
    
    -- Model Information
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    feature_version VARCHAR(50) NOT NULL,
    
    -- Explainability
    key_factors JSONB DEFAULT '[]',
    explanation_summary TEXT,
    confidence_level DECIMAL(5,2),
    
    -- Validation
    actual_outcome VARCHAR(50), -- For model validation
    outcome_date DATE,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) -- Usually system user
);

CREATE INDEX idx_ai_risk_case ON ai_risk_assessments(case_id);
CREATE INDEX idx_ai_risk_score ON ai_risk_assessments(risk_score DESC);
CREATE INDEX idx_ai_risk_created ON ai_risk_assessments(created_at DESC);
```

### 6. Audit & Compliance Models

#### Audit Log Entity
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event Details
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL, -- AUTH, DATA, BUSINESS, SYSTEM
    event_severity VARCHAR(20) DEFAULT 'info' CHECK (event_severity IN ('debug', 'info', 'warning', 'error', 'critical')),
    
    -- Entity Information
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    entity_data JSONB DEFAULT '{}',
    
    -- User Context
    user_id UUID REFERENCES users(id),
    user_role VARCHAR(100),
    organization_id UUID REFERENCES organizations(id),
    
    -- System Context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    
    -- Change Details
    action VARCHAR(200) NOT NULL,
    previous_values JSONB DEFAULT '{}',
    new_values JSONB DEFAULT '{}',
    changed_fields TEXT[],
    
    -- Compliance
    compliance_flags JSONB DEFAULT '{}',
    retention_period INTEGER DEFAULT 2555, -- Days (7 years default)
    
    -- Timestamps
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Partitioning by month for performance
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_occurred ON audit_logs(occurred_at DESC);
CREATE INDEX idx_audit_event_type ON audit_logs(event_type);
```

#### Compliance Report Entity
```sql
CREATE TABLE compliance_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    
    -- Report Details
    report_type VARCHAR(100) NOT NULL, -- RBI, DPDP, INTERNAL
    report_period_start DATE NOT NULL,
    report_period_end DATE NOT NULL,
    
    -- Content
    report_data JSONB NOT NULL,
    summary_statistics JSONB DEFAULT '{}',
    key_findings TEXT[],
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'submitted')),
    generated_by UUID REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id),
    submitted_by UUID REFERENCES users(id),
    
    -- Timestamps
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    submitted_at TIMESTAMP,
    
    -- File Storage
    report_file_path VARCHAR(500),
    checksum VARCHAR(64),
    file_size BIGINT
);
```

## Data Relationships

### Primary Relationships
```
Organizations 1:N Users
Organizations 1:N Cases
Users 1:N Cases (assigned_agent)
Customers 1:N Cases
Cases 1:N Payments
Cases 1:N Communications
Cases 1:N CaseHistory
Cases 1:1 AI Risk Assessment (latest)
```

### Data Integrity Rules
1. **Cascade Deletes:** Soft delete only for audit compliance
2. **Foreign Key Constraints:** Enforced at database level
3. **Unique Constraints:** Business-critical uniqueness
4. **Check Constraints:** Data validation rules
5. **Triggers:** Audit trail automation

## Performance Optimization

### Indexing Strategy
- Primary keys on all tables
- Foreign key columns indexed
- Frequently queried columns indexed
- Composite indexes for complex queries
- Partial indexes for filtered queries

### Partitioning Strategy
- Audit logs: Monthly partitioning
- Communications: Monthly partitioning by created_at
- Case history: Monthly partitioning
- Payment records: Monthly partitioning

### Data Archival
- Move data older than 2 years to cold storage
- Maintain summary tables for historical analytics
- Implement data lifecycle policies
- Automated archival processes