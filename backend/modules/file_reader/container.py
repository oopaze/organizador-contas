from dependency_injector import containers, providers
from django.conf import settings

from modules.file_reader.factories.ai_call import AICallFactory
from modules.file_reader.factories.bill import BillFactory
from modules.file_reader.factories.bill_sub_transaction import BillSubTransactionFactory
from modules.file_reader.factories.file import FileFactory
from modules.file_reader.models import File
from modules.ai.models import AICall
from modules.transactions.models import Transaction, SubTransaction
from modules.file_reader.repositories.ai_call import AICallRepository
from modules.file_reader.repositories.file import FileRepository
from modules.file_reader.repositories.bill import BillRepository
from modules.file_reader.repositories.bill_sub_transaction import BillSubTransactionRepository
from modules.file_reader.serializers.ai_call import AICallSerializer
from modules.file_reader.serializers.bill import BillSerializer
from modules.file_reader.serializers.bill_sub_transaction import BillSubTransactionSerializer
from modules.file_reader.serializers.file import FileSerializer
from modules.file_reader.use_cases.list_bills import ListBillsUseCase
from modules.file_reader.use_cases.load_bills_with_transactions import LoadBillsWithTransactionsUseCase
from modules.file_reader.use_cases.transpose_file_bill_to_models import TransposeFileBillToModelsUseCase
from modules.file_reader.use_cases.upload_file import UploadFileUseCase
from modules.file_reader.use_cases.upload_sheet import UploadSheetUseCase
from modules.file_reader.use_cases.remover_pdf_password import RemovePDFPasswordUseCase


class FileReaderContainer(containers.DeclarativeContainer):
    # SERIALIZERS
    ai_call_serializer = providers.Factory(AICallSerializer)
    file_serializer = providers.Factory(FileSerializer, ai_call_serializer=ai_call_serializer)
    bill_sub_transaction_serializer = providers.Factory(BillSubTransactionSerializer)
    bill_serializer = providers.Factory(BillSerializer, bill_sub_transaction_serializer=bill_sub_transaction_serializer)

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
        bill_serializer=bill_serializer,
        bill_sub_transaction_repository=bill_sub_transaction_repository,
        bill_sub_transaction_factory=bill_sub_transaction_factory,
        file_repository=file_repository,
    )

    ask_use_case = providers.Dependency(default=None)

    remove_pdf_password_use_case = providers.Factory(RemovePDFPasswordUseCase)

    upload_file_use_case = providers.Factory(
        UploadFileUseCase,
        file_repository=file_repository,
        file_factory=file_factory,
        file_serializer=file_serializer,
        transpose_file_bill_to_models_use_case=transpose_file_bill_to_models_use_case,
        ai_call_repository=ai_call_repository,
        ai_call_factory=ai_call_factory,
        ask_use_case=ask_use_case,
        remove_pdf_password_use_case=remove_pdf_password_use_case,
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

    upload_sheet_use_case = providers.Factory(
        UploadSheetUseCase,
        file_repository=file_repository,
        file_factory=file_factory,
        file_serializer=file_serializer,
    )
