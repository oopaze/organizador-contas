import logging

from celery import shared_task

from modules.ai.container import AIContainer
from modules.ai.types import LlmModels
from modules.file_reader.container import FileReaderContainer
from modules.file_reader.use_cases.upload_sheet import (
    SPREADSHEET_PROMPT,
    USER_PROVIDED_DESCRIPTION_PROMPT,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_sheet_upload(
    self,
    file_id: int,
    user_id: int,
    model: str = LlmModels.DEEPSEEK_CHAT.name,
    user_provided_description: str = None,
):
    """
    Celery task to process spreadsheet upload asynchronously.
    
    This task:
    1. Loads the saved file from database
    2. Extracts text from spreadsheet
    3. Calls AI to process the data
    4. Creates transactions from the AI response
    """
    logger.info(f"[Task:UploadSheet] Starting processing for file_id={file_id}, user_id={user_id}, model={model}")
    
    try:
        # Initialize containers
        ask_use_case = AIContainer().ask_use_case()
        container = FileReaderContainer(ask_use_case=ask_use_case)
        
        # Get repositories and use cases
        file_repository = container.file_repository()
        ai_call_repository = container.ai_call_repository()
        transpose_use_case = container.transpose_file_bill_to_models_use_case()
        
        # Load the saved file
        saved_file = file_repository.get(file_id)
        if not saved_file:
            logger.error(f"[Task:UploadSheet] File not found: {file_id}")
            return {"status": "error", "message": "File not found"}

        logger.info(f"[Task:UploadSheet] File loaded: {saved_file.url}")
        
        # Extract text from spreadsheet
        logger.info(f"[Task:UploadSheet] Extracting text from spreadsheet...")
        spreadsheet_text = saved_file.extract_text_from_spreadsheet()
        logger.info(f"[Task:UploadSheet] Extracted {len(spreadsheet_text)} characters")
        
        # Build prompt
        prompt = [SPREADSHEET_PROMPT]
        if user_provided_description:
            logger.info(f"[Task:UploadSheet] User description: {user_provided_description[:100]}...")
            prompt.append(USER_PROVIDED_DESCRIPTION_PROMPT.format(
                user_provided_description=user_provided_description
            ))
        prompt.append(f"Here is the spreadsheet content:\n{spreadsheet_text}")
        
        # Call AI
        logger.info(f"[Task:UploadSheet] Calling AI with model: {model}...")
        ai_call_id = ask_use_case.execute(prompt, response_format="json_object", model=model)
        logger.info(f"[Task:UploadSheet] AI call completed with id: {ai_call_id}")

        # Update file with AI info
        ai_call = ai_call_repository.get(ai_call_id)
        logger.info(f"[Task:UploadSheet] AI response: {ai_call.response}")
        saved_file.update_ai_info(ai_call)
        file_repository.update(saved_file)
        logger.info(f"[Task:UploadSheet] File updated with AI info")

        # Transpose to models (create transactions)
        logger.info(f"[Task:UploadSheet] Creating transactions...")
        transpose_use_case.execute(file_id, user_id)
        logger.info(f"[Task:UploadSheet] Processing completed successfully for file: {file_id}")
        
        return {"status": "success", "file_id": file_id}
        
    except Exception as e:
        logger.error(f"[Task:UploadSheet] Error processing file {file_id}: {type(e).__name__}: {e}")
        # Retry on failure
        raise self.retry(exc=e)

