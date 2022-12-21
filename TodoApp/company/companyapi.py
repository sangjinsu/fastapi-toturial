from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def get_company_name():
    return dict(
        company_name='Example Company'
    )


@router.get('/employees')
async def number_of_employees():
    return 34
