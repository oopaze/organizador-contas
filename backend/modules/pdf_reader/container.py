from dependency_injector import containers, providers
from django.conf import settings

from modules.pdf_reader.factories.ai_call import AICallFactory
from modules.pdf_reader.factories.bill import BillFactory
from modules.pdf_reader.factories.bill_sub_transaction import BillSubTransactionFactory
from modules.pdf_reader.factories.file import FileFactory
from modules.pdf_reader.gateways.google_llm import GoogleLLMGateway
from modules.pdf_reader.models import AICall, File
from modules.transactions.models import Transaction, SubTransaction
from modules.pdf_reader.repositories.ai_call import AICallRepository
from modules.pdf_reader.repositories.file import FileRepository
from modules.pdf_reader.repositories.bill import BillRepository
from modules.pdf_reader.repositories.bill_sub_transaction import BillSubTransactionRepository
from modules.pdf_reader.serializers.ai_call import AICallSerializer
from modules.pdf_reader.serializers.bill import BillSerializer
from modules.pdf_reader.serializers.bill_sub_transaction import BillSubTransactionSerializer
from modules.pdf_reader.serializers.file import FileSerializer
from modules.pdf_reader.use_cases.list_bills import ListBillsUseCase
from modules.pdf_reader.use_cases.load_bills_with_transactions import LoadBillsWithTransactionsUseCase
from modules.pdf_reader.use_cases.transpose_file_bill_to_models import TransposeFileBillToModelsUseCase
from modules.pdf_reader.use_cases.upload_file import UploadFileUseCase


class PDFReaderContainer(containers.DeclarativeContainer):
    # SERIALIZERS
    ai_call_serializer = providers.Factory(AICallSerializer)
    file_serializer = providers.Factory(FileSerializer, ai_call_serializer=ai_call_serializer)
    bill_sub_transaction_serializer = providers.Factory(BillSubTransactionSerializer)
    bill_serializer = providers.Factory(BillSerializer, bill_sub_transaction_serializer=bill_sub_transaction_serializer)

    # GATEWAYS
    google_llm_gateway = providers.Factory(
        GoogleLLMGateway, api_key=settings.GOOGLE_AI_API_KEY
    )

    # FACTORIES
    ai_call_factory = providers.Factory(AICallFactory)
    file_factory = providers.Factory(FileFactory, ai_call_factory=ai_call_factory)
    bill_factory = providers.Factory(BillFactory, file_factory=file_factory)
    bill_sub_transaction_factory = providers.Factory(BillSubTransactionFactory)

    # REPOSITORIES
    ai_call_repository = providers.Factory(AICallRepository, model=AICall, ai_call_factory=ai_call_factory)
    file_repository = providers.Factory(FileRepository, model=File, file_factory=file_factory)
    bill_repository = providers.Factory(BillRepository, model=Transaction, bill_factory=bill_factory)
    bill_sub_transaction_repository = providers.Factory(
        BillSubTransactionRepository,
        model=SubTransaction,
        bill_sub_transaction_factory=bill_sub_transaction_factory,
    )

    # USE CASES
    transpose_file_bill_to_models_use_case = providers.Factory(
        TransposeFileBillToModelsUseCase,
        bill_repository=bill_repository,
        bill_factory=bill_factory,
        bill_sub_transaction_repository=bill_sub_transaction_repository,
        bill_sub_transaction_factory=bill_sub_transaction_factory,
        file_repository=file_repository,
    )

    upload_file_use_case = providers.Factory(
        UploadFileUseCase,
        file_repository=file_repository,
        file_factory=file_factory,
        google_llm_gateway=google_llm_gateway,
        file_serializer=file_serializer,
        transpose_file_bill_to_models_use_case=transpose_file_bill_to_models_use_case,
        ai_call_repository=ai_call_repository,
        ai_call_factory=ai_call_factory,
    )

    load_bills_with_transactions_use_case = providers.Factory(
        LoadBillsWithTransactionsUseCase,
        bill_repository=bill_repository,
        bill_sub_transaction_repository=bill_sub_transaction_repository,
        bill_serializer=bill_serializer,
    )

    list_bills_use_case = providers.Factory(
        ListBillsUseCase,
        bill_repository=bill_repository,
        bill_serializer=bill_serializer,
    )
