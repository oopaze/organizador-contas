SCOPED_TABLES_CTE = """\
WITH
  me AS (SELECT %(user_id)s::bigint AS id),
  transactions_transaction AS (
    SELECT * FROM public.transactions_transaction
    WHERE user_id = (SELECT id FROM me) AND deleted_at IS NULL
  ),
  transactions_actor AS (
    SELECT * FROM public.transactions_actor
    WHERE user_id = (SELECT id FROM me) AND deleted_at IS NULL
  ),
  transactions_subtransaction AS (
    SELECT s.* FROM public.transactions_subtransaction s
    JOIN public.transactions_transaction t ON s.transaction_id = t.id
    WHERE t.user_id = (SELECT id FROM me) AND s.deleted_at IS NULL
  ),
  file_reader_file AS (
    SELECT * FROM public.file_reader_file
    WHERE user_id = (SELECT id FROM me)
  ),
  loans_loan AS (
    SELECT * FROM public.loans_loan
    WHERE user_id = (SELECT id FROM me) AND deleted_at IS NULL
  ),
  loans_loanpayment AS (
    SELECT p.* FROM public.loans_loanpayment p
    JOIN public.loans_loan l ON p.loan_id = l.id
    WHERE l.user_id = (SELECT id FROM me) AND p.deleted_at IS NULL
  )
"""


class QueryScoperService:
    """Wraps a user-supplied SELECT in CTEs that shadow real table names with
    user-scoped, soft-delete-filtered versions, then caps the result with a
    LIMIT.
    """

    def scope(
        self, query: str, *, user_id: int, row_limit: int = 1000
    ) -> tuple[str, dict]:
        outer_limit = row_limit + 1  # +1 so the gateway can detect truncation
        wrapped = (
            f"{SCOPED_TABLES_CTE}"
            f"SELECT * FROM (\n"
            f"{query}\n"
            f") AS _user_query LIMIT {outer_limit}\n"
            f"-- end-of-wrap: {query}"
        )
        return wrapped, {"user_id": user_id}
