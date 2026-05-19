from dependency_injector import containers, providers

from modules.loans.factories.loan import LoanFactory
from modules.loans.factories.loan_payment import LoanPaymentFactory
from modules.loans.models import Loan, LoanPayment
from modules.loans.repositories.loan import LoanRepository
from modules.loans.repositories.loan_payment import LoanPaymentRepository
from modules.loans.serializers.loan import LoanSerializer
from modules.loans.serializers.loan_payment import LoanPaymentSerializer
from modules.loans.use_cases.loan import (
    CreateLoanUseCase,
    GetLoanUseCase,
    ListLoansUseCase,
    UpdateLoanUseCase,
    DeleteLoanUseCase,
    LoanStatsUseCase,
)
from modules.loans.use_cases.loan_payment import (
    CreateLoanPaymentUseCase,
    GetLoanPaymentUseCase,
    ListLoanPaymentsUseCase,
    UpdateLoanPaymentUseCase,
    DeleteLoanPaymentUseCase,
)
from modules.loans.use_cases.parse_pix_receipt import ParsePixReceiptUseCase


class LoansContainer(containers.DeclarativeContainer):
    # DEPENDENCIES (injected from views — AI bits cross module boundaries)
    ask_use_case = providers.Dependency()
    ai_call_repository = providers.Dependency()

    # FACTORIES
    loan_payment_factory = providers.Factory(LoanPaymentFactory)
    loan_factory = providers.Factory(LoanFactory, loan_payment_factory=loan_payment_factory)

    # REPOSITORIES
    loan_repository = providers.Factory(LoanRepository, model=Loan, loan_factory=loan_factory)
    loan_payment_repository = providers.Factory(
        LoanPaymentRepository, model=LoanPayment, loan_payment_factory=loan_payment_factory
    )

    # SERIALIZERS
    loan_payment_serializer = providers.Factory(LoanPaymentSerializer)
    loan_serializer = providers.Factory(
        LoanSerializer, loan_payment_serializer=loan_payment_serializer
    )

    # USE CASES — loan
    create_loan_use_case = providers.Factory(
        CreateLoanUseCase,
        loan_repository=loan_repository,
        loan_factory=loan_factory,
        loan_serializer=loan_serializer,
    )
    get_loan_use_case = providers.Factory(
        GetLoanUseCase, loan_repository=loan_repository, loan_serializer=loan_serializer
    )
    list_loans_use_case = providers.Factory(
        ListLoansUseCase, loan_repository=loan_repository, loan_serializer=loan_serializer
    )
    update_loan_use_case = providers.Factory(
        UpdateLoanUseCase, loan_repository=loan_repository, loan_serializer=loan_serializer
    )
    delete_loan_use_case = providers.Factory(DeleteLoanUseCase, loan_repository=loan_repository)
    loan_stats_use_case = providers.Factory(LoanStatsUseCase, loan_repository=loan_repository)

    # USE CASES — loan_payment
    create_loan_payment_use_case = providers.Factory(
        CreateLoanPaymentUseCase,
        loan_payment_repository=loan_payment_repository,
        loan_repository=loan_repository,
        loan_payment_factory=loan_payment_factory,
        loan_payment_serializer=loan_payment_serializer,
    )
    get_loan_payment_use_case = providers.Factory(
        GetLoanPaymentUseCase,
        loan_payment_repository=loan_payment_repository,
        loan_payment_serializer=loan_payment_serializer,
    )
    list_loan_payments_use_case = providers.Factory(
        ListLoanPaymentsUseCase,
        loan_payment_repository=loan_payment_repository,
        loan_payment_serializer=loan_payment_serializer,
    )
    update_loan_payment_use_case = providers.Factory(
        UpdateLoanPaymentUseCase,
        loan_payment_repository=loan_payment_repository,
        loan_repository=loan_repository,
        loan_payment_serializer=loan_payment_serializer,
    )
    delete_loan_payment_use_case = providers.Factory(
        DeleteLoanPaymentUseCase,
        loan_payment_repository=loan_payment_repository,
        loan_repository=loan_repository,
    )

    # PIX parser (depends on AI bits injected from outside)
    parse_pix_receipt_use_case = providers.Factory(
        ParsePixReceiptUseCase,
        ask_use_case=ask_use_case,
        ai_call_repository=ai_call_repository,
    )
