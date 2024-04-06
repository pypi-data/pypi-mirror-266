from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import DatabaseError, IntegrityError
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class BaseView(APIView):
    @staticmethod
    def handle_exception(e, action="unknown action"):
        if isinstance(e, IntegrityError):
            logger.error(f"Integrity error occurred during {action}: {str(e)}")
            return Response({"status": f"{action} failed: Integrity error, please check the data", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(e, DatabaseError):
            logger.error(f"Database error occurred during {action}: {str(e)}")
            return Response({"status": f"{action} failed: Database error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Unexpected error occurred during {action}: {str(e)}")
            return Response({"status": f"{action} failed", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)