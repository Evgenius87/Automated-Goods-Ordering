
from fastapi import HTTPException,APIRouter, Depends, status
from sqlalchemy.orm import Session


from src.schemas import ProviderResponse
from src.database.db_connection import get_db
from src.repository import providers as prov
from src.services.roles import access_ABCU, access_A, access_ABC




router = APIRouter(prefix="/providers", tags=["providers"])

@router.get("/", 
            dependencies=[Depends(access_ABC)],
            response_model=list[ProviderResponse])
async def get_providers(db: Session = Depends(get_db)):
    providers = await prov.get_providers(db)
    if not providers:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail="Providers not found")
    return providers



@router.delete("/delete/{id}",
               dependencies=[Depends(access_ABC)],)
async def delete_provider(id: int, db: Session=Depends(get_db)):
    return await prov.delete_provider(id, db)




