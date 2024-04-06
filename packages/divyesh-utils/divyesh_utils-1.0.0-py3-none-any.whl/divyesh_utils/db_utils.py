from django.db import connection

def execute_query(query, params=None, fetchone=False, procedure_call=False):
    """Utility function to execute a database query."""
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if procedure_call:
            # For procedure calls, we might not need to fetch results.
            return None
        return cursor.fetchone() if fetchone else cursor.fetchall()