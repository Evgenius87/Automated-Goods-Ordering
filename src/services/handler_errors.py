import functools
import logging

from fastapi import HTTPException, status


logger = logging.getLogger(__name__)

def handle_errors(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        logging.basicConfig(level=logging.INFO)
        try:
            return await method(self, *args, **kwargs)
        except Exception as e:
            logger.info(f"Something wrong wit method '{method.__name__}': {e}")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"we have a problem whith {method.__name__}")
    return wrapper


