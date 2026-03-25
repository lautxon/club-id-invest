# Club ID Invest - ERD Diagram

## Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ LEGAL_ENTITIES : "owns"
    USERS ||--o{ MEMBERSHIPS : "has"
    USERS ||--o{ INVESTMENTS : "makes"
    USERS ||--o{ CONTRACTS : "signs"
    USERS ||--o{ AUDIT_LOGS : "generates"
    
    LEGAL_ENTITIES ||--o{ INVESTMENTS : "invests in"
    LEGAL_ENTITIES ||--o{ CONTRACTS : "party to"
    
    MEMBERSHIPS }o--|| USERS : "belongs to"
    
    PROJECTS ||--o{ INVESTMENTS : "receives"
    PROJECTS ||--o{ PROJECT_DOCUMENTS : "contains"
    PROJECTS ||--o{ CONTRACTS : "has"
    
    INVESTMENTS }o--|| USERS : "made by"
    INVESTMENTS }o--|| PROJECTS : "in"
    INVESTMENTS }o--o{ LEGAL_ENTITIES : "via"
    INVESTMENTS ||--o{ INVESTMENT_TRANSACTIONS : "has"
    INVESTMENTS ||--o| CONTRACTS : "linked to"
    
    INVESTMENT_TRANSACTIONS }o--|| INVESTMENTS : "belongs to"
    
    CONTRACTS }o--|| PROJECTS : "for"
    CONTRACTS }o--o| INVESTMENTS : "covers"
    CONTRACTS }o--o{ LEGAL_ENTITIES : "involves"
    CONTRACTS }o--|| USERS : "signed by"
    
    AUDIT_LOGS }o--|| USERS : "actor"

    USERS {
        int id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        string phone
        datetime date_of_birth
        enum role "investor, project_manager, admin, super_admin"
        boolean is_active
        boolean is_verified
        datetime last_login_at
        datetime created_at
        datetime updated_at
    }

    LEGAL_ENTITIES {
        int id PK
        int user_id FK
        string legal_name
        string trade_name
        string tax_id UK
        string entity_type "SA, SRL, Trust, etc."
        string registration_number
        string jurisdiction
        datetime incorporation_date
        text registered_address
        string bank_name
        string bank_account_number
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    MEMBERSHIPS {
        int id PK
        int user_id FK
        enum category "cebollitas, primera_div, senior"
        enum status "active, inactive, churned, suspended"
        datetime join_date
        datetime last_activity_date
        datetime category_changed_at
        string previous_category
        float penalty_amount
        int total_investments_count
        float total_invested_amount
        int active_investments_count
        datetime created_at
        datetime updated_at
    }

    PROJECTS {
        int id PK
        string title
        text description
        string short_description
        enum category "level_1, level_2, level_3"
        float target_amount
        float minimum_investment
        float maximum_investment
        float raised_amount
        float raised_percent
        int investor_count
        float club_contribution_percent
        float club_contribution_amount
        boolean club_contribution_triggered
        datetime club_contribution_triggered_at
        enum status "draft, funding, funded, active, completed, cancelled"
        datetime start_date
        datetime end_date
        datetime funding_deadline
        string address
        string city
        float expected_return_percent
        int expected_duration_months
        int risk_rating
        datetime created_at
        datetime updated_at
        datetime published_at
    }

    PROJECT_DOCUMENTS {
        int id PK
        int project_id FK
        string title
        string document_type "legal, financial, technical, marketing"
        string file_path
        string file_name
        int file_size
        string mime_type
        boolean is_public
        datetime created_at
        int uploaded_by FK
    }

    INVESTMENTS {
        int id PK
        int user_id FK
        int project_id FK
        int legal_entity_id FK
        float investment_amount
        string currency "USD"
        enum status "pending, confirmed, active, returned, written_off"
        string payment_method
        string payment_reference
        datetime payment_confirmed_at
        boolean is_club_contribution
        text club_contribution_trigger_reason
        float expected_return_percent
        float expected_return_amount
        float actual_return_amount
        datetime return_paid_at
        text notes
        datetime created_at
        datetime updated_at
        datetime confirmed_at
    }

    INVESTMENT_TRANSACTIONS {
        int id PK
        int investment_id FK
        string transaction_type "PAYMENT, RETURN, PENALTY, REFUND, CLUB_CONTRIBUTION, FEE"
        float amount
        string currency "USD"
        string status "pending, processing, completed, failed, cancelled"
        string payment_method
        string payment_reference
        string external_transaction_id
        text description
        datetime created_at
        datetime processed_at
    }

    CONTRACTS {
        int id PK
        int project_id FK
        int investment_id FK
        int legal_entity_id FK
        int signed_by_user_id FK
        string contract_number UK
        string contract_type "FIDEICOMISO, INVESTMENT_AGREEMENT, CLUB_CONTRIBUTION, AMENDMENT"
        string title
        text description
        float principal_amount
        float interest_rate
        int term_months
        string currency "USD"
        enum status "draft, pending_signature, signed, cancelled"
        string template_path
        string generated_pdf_path
        string signed_pdf_path
        string signature_hash
        datetime signature_timestamp
        string signature_ip_address
        string signature_user_agent
        boolean is_club_contribution_contract
        datetime created_at
        datetime updated_at
        datetime sent_at
        datetime signed_at
        datetime expires_at
    }

    AUDIT_LOGS {
        int id PK
        int actor_user_id FK
        enum action "CREATE, UPDATE, DELETE, LOGIN, LOGOUT, INVEST, WITHDRAW, SIGN_CONTRACT, STATUS_CHANGE"
        string resource_type "user, investment, project, contract, membership"
        int resource_id
        json old_values
        json new_values
        text changes_summary
        string ip_address
        string user_agent
        string request_id
        json metadata
        string severity "INFO, WARNING, ERROR, CRITICAL"
        datetime created_at
    }
```

## Business Rules Summary

### Co-Investment Tiers

| Tier | Min Raised % | Min Months | Club Contribution % |
|------|-------------|------------|---------------------|
| Cebollitas | >55% | 3 | 45% |
| 1ra Div | >65% | 6 | 35% |
| Senior | >75% | 9 | 25% |

### Membership Lifecycle

| Condition | Action |
|-----------|--------|
| 60 days inactive | Mark 'inactive', charge $50 penalty |
| 180 days inactive | Mark 'churned' |

### Constraints

- Maximum 5 active investments per user
- Maximum 50 investors per project
- Audit log retention: 7 years (2555 days)
