"""
Contract Service
Handles contract generation and electronic signature.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, List
import logging
import os

from app.core.config import ContractStatusEnum, AuditActionEnum
from app.models.contracts import Contract
from app.models.projects import Project
from app.models.investments import Investment
from app.models.legal_entities import LegalEntity
from app.models.audit_logs import AuditLog

logger = logging.getLogger(__name__)


class ContractService:
    """
    Service for generating and managing legal contracts.
    
    Features:
    - Generate PDF contracts with dynamic data
    - Electronic signature (simulated)
    - Contract status tracking
    """

    def __init__(self, db: Session, template_path: str = "templates/contracts"):
        self.db = db
        self.template_path = template_path

    def generate_contract(
        self,
        project_id: int,
        investment_id: Optional[int] = None,
        legal_entity_id: Optional[int] = None,
        contract_type: str = "FIDEICOMISO",
        title: Optional[str] = None,
    ) -> Contract:
        """
        Generate a new contract for an investment.
        
        Args:
            project_id: ID of the project
            investment_id: ID of the related investment (optional for Club contributions)
            legal_entity_id: ID of the legal entity
            contract_type: Type of contract (FIDEICOMISO, INVESTMENT_AGREEMENT, etc.)
            title: Optional custom title
        
        Returns:
            Generated Contract object
        """
        # Get project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get investment if provided
        investment = None
        if investment_id:
            investment = self.db.query(Investment).filter(Investment.id == investment_id).first()
            if not investment:
                raise ValueError(f"Investment {investment_id} not found")

        # Get legal entity if provided
        legal_entity = None
        if legal_entity_id:
            legal_entity = self.db.query(LegalEntity).filter(LegalEntity.id == legal_entity_id).first()

        # Generate contract number
        contract_number = self._generate_contract_number(project_id, contract_type)

        # Determine principal amount
        principal_amount = investment.investment_amount if investment else 0.0

        # Create contract
        contract = Contract(
            project_id=project_id,
            investment_id=investment_id,
            legal_entity_id=legal_entity_id,
            contract_number=contract_number,
            contract_type=contract_type,
            title=title or f"{contract_type} - {project.title}",
            description=self._generate_contract_description(project, investment, legal_entity),
            principal_amount=principal_amount,
            interest_rate=project.expected_return_percent,
            term_months=project.expected_duration_months,
            currency="USD",
            status=ContractStatusEnum.DRAFT,
            template_path=os.path.join(self.template_path, f"{contract_type.lower()}.html"),
            is_club_contribution_contract=investment.is_club_contribution if investment else False,
        )
        self.db.add(contract)
        self.db.flush()

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.CREATE,
            resource_type="contract",
            resource_id=contract.id,
            actor_user_id=investment.user_id if investment else None,
            new_values={
                "contract_number": contract_number,
                "project_id": project_id,
                "investment_id": investment_id,
            },
            severity="INFO",
        )
        self.db.add(audit_entry)

        logger.info(f"Generated contract {contract.id} ({contract_number}) for project {project_id}")
        return contract

    def _generate_contract_number(self, project_id: int, contract_type: str) -> str:
        """Generate unique contract number."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{contract_type[:3].upper()}-{project_id}-{timestamp}"

    def _generate_contract_description(
        self,
        project: Project,
        investment: Optional[Investment],
        legal_entity: Optional[LegalEntity],
    ) -> str:
        """Generate contract description based on context."""
        base_desc = f"Contrato de {project.title}"
        
        if legal_entity:
            base_desc += f" con {legal_entity.legal_name}"
        
        if investment:
            base_desc += f" por USD {investment.investment_amount:,.2f}"
        
        return base_desc

    def generate_pdf(self, contract_id: int) -> Dict[str, any]:
        """
        Generate PDF from contract template.
        
        This is a skeleton implementation. In production, use:
        - WeasyPrint or ReportLab for PDF generation
        - Jinja2 templates for dynamic content
        
        Returns:
            Dict with PDF path and status
        """
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {"success": False, "error": "Contract not found"}

        if contract.status == ContractStatusEnum.CANCELLED:
            return {"success": False, "error": "Cannot generate PDF for cancelled contract"}

        # Create output directory if needed
        output_dir = "generated_contracts"
        os.makedirs(output_dir, exist_ok=True)

        # Generate PDF path
        pdf_filename = f"{contract.contract_number}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        # TODO: Implement actual PDF generation
        # Example with WeasyPrint:
        # from weasyprint import HTML
        # html_content = self._render_template(contract)
        # HTML(string=html_content).write_pdf(pdf_path)
        
        # For now, just mark the path
        contract.generated_pdf_path = pdf_path
        
        # Update status if still in draft
        if contract.status == ContractStatusEnum.DRAFT:
            contract.status = ContractStatusEnum.PENDING_SIGNATURE

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.UPDATE,
            resource_type="contract",
            resource_id=contract.id,
            changes_summary=f"Generated PDF: {pdf_path}",
            severity="INFO",
        )
        self.db.add(audit_entry)

        logger.info(f"Generated PDF for contract {contract.id}: {pdf_path}")
        return {
            "success": True,
            "contract_id": contract.id,
            "pdf_path": pdf_path,
            "status": contract.status.value,
        }

    def _render_template(self, contract: Contract) -> str:
        """
        Render contract template with dynamic data.
        
        Uses Jinja2 for template rendering.
        """
        from jinja2 import Environment, FileSystemLoader
        
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.load_template(f"{contract.contract_type.lower()}.html")
        
        # Gather context data
        project = self.db.query(Project).filter(Project.id == contract.project_id).first()
        investment = None
        if contract.investment_id:
            investment = self.db.query(Investment).filter(Investment.id == contract.investment_id).first()
        
        legal_entity = None
        if contract.legal_entity_id:
            legal_entity = self.db.query(LegalEntity).filter(LegalEntity.id == contract.legal_entity_id).first()
        
        user = None
        if investment and investment.user_id:
            from app.models.users import User
            user = self.db.query(User).filter(User.id == investment.user_id).first()
        
        # Render template
        html_content = template.render(
            contract=contract,
            project=project,
            investment=investment,
            legal_entity=legal_entity,
            user=user,
            generated_at=datetime.utcnow().isoformat(),
        )
        
        return html_content

    def send_for_signature(self, contract_id: int, user_id: int) -> Dict[str, any]:
        """
        Send contract for electronic signature.
        
        Args:
            contract_id: ID of the contract
            user_id: ID of the user who will sign
        
        Returns:
            Dict with status and next steps
        """
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {"success": False, "error": "Contract not found"}

        if contract.status != ContractStatusEnum.DRAFT:
            return {"success": False, "error": f"Contract is in {contract.status.value} status"}

        if not contract.generated_pdf_path:
            return {"success": False, "error": "PDF not generated yet"}

        # Update status
        contract.status = ContractStatusEnum.PENDING_SIGNATURE
        contract.sent_at = datetime.utcnow()

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.UPDATE,
            resource_type="contract",
            resource_id=contract.id,
            actor_user_id=user_id,
            changes_summary="Sent for signature",
            severity="INFO",
        )
        self.db.add(audit_entry)

        logger.info(f"Contract {contract.id} sent for signature to user {user_id}")
        return {
            "success": True,
            "contract_id": contract.id,
            "status": ContractStatusEnum.PENDING_SIGNATURE.value,
            "message": "Contract sent for signature",
        }

    def sign_contract(
        self,
        contract_id: int,
        user_id: int,
        ip_address: str,
        user_agent: str,
    ) -> Dict[str, any]:
        """
        Sign contract electronically.
        
        Args:
            contract_id: ID of the contract
            user_id: ID of the signing user
            ip_address: IP address of the signer
            user_agent: User agent string
        
        Returns:
            Dict with signature confirmation
        """
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {"success": False, "error": "Contract not found"}

        if contract.status != ContractStatusEnum.PENDING_SIGNATURE:
            return {"success": False, "error": f"Contract is in {contract.status.value} status"}

        # Generate signature hash
        signature_hash = contract.generate_signature_hash(user_id, ip_address, user_agent)
        
        # Update contract
        contract.status = ContractStatusEnum.SIGNED
        contract.signed_at = datetime.utcnow()
        contract.signed_by_user_id = user_id
        contract.signature_hash = signature_hash
        contract.signature_timestamp = datetime.utcnow()
        contract.signature_ip_address = ip_address
        contract.signature_user_agent = user_agent

        # Copy to signed PDF path
        if contract.generated_pdf_path:
            contract.signed_pdf_path = contract.generated_pdf_path.replace(
                "generated_contracts/",
                "generated_contracts/signed_"
            )

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.SIGN_CONTRACT,
            resource_type="contract",
            resource_id=contract.id,
            actor_user_id=user_id,
            new_values={
                "signature_hash": signature_hash[:16] + "...",
                "ip_address": ip_address,
            },
            severity="INFO",
        )
        self.db.add(audit_entry)

        logger.info(f"Contract {contract.id} signed by user {user_id}")
        return {
            "success": True,
            "contract_id": contract.id,
            "contract_number": contract.contract_number,
            "signed_at": contract.signed_at.isoformat(),
            "signature_hash": signature_hash,
        }

    def cancel_contract(self, contract_id: int, user_id: int, reason: str) -> Dict[str, any]:
        """Cancel a contract."""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return {"success": False, "error": "Contract not found"}

        if contract.status == ContractStatusEnum.SIGNED:
            return {"success": False, "error": "Cannot cancel a signed contract"}

        old_status = contract.status
        contract.status = ContractStatusEnum.CANCELLED

        # Audit log
        audit_entry = AuditLog.log_action(
            action=AuditActionEnum.STATUS_CHANGE,
            resource_type="contract",
            resource_id=contract.id,
            actor_user_id=user_id,
            old_values={"status": old_status.value},
            new_values={"status": "cancelled"},
            changes_summary=f"Cancelled: {reason}",
            severity="WARNING",
        )
        self.db.add(audit_entry)

        logger.info(f"Contract {contract.id} cancelled by user {user_id}: {reason}")
        return {"success": True, "contract_id": contract.id}

    def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Get contract by ID."""
        return self.db.query(Contract).filter(Contract.id == contract_id).first()

    def get_contracts_for_user(self, user_id: int) -> List[Contract]:
        """Get all contracts for a user."""
        return (
            self.db.query(Contract)
            .filter(Contract.signed_by_user_id == user_id)
            .order_by(Contract.created_at.desc())
            .all()
        )

    def get_pending_contracts(self) -> List[Contract]:
        """Get all contracts pending signature."""
        return (
            self.db.query(Contract)
            .filter(Contract.status == ContractStatusEnum.PENDING_SIGNATURE)
            .order_by(Contract.created_at)
            .all()
        )
