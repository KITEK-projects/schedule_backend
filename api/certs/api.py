from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from app.auth import JWTAuth
from certs.models import Cert
from certs.schemas import CertCreate, CertRetrieve


router = Router()
jwt_auth = JWTAuth()


@router.post("", auth=jwt_auth, response=CertRetrieve)
def create_cert(request, data: CertCreate):
    cert = Cert.objects.create(**data.model_dump())

    cert_out = CertRetrieve.from_orm(cert)
    cert_out.status = cert.get_status_display()
    return cert_out


@router.get("", auth=jwt_auth, response=list[CertRetrieve])
def retrieve_cert(request):
    user = request.auth
    certs = Cert.objects.filter(user=user)

    out = []
    for cert in certs:
        cert_data = CertRetrieve.from_orm(cert)

        cert_data.status = cert.get_status_display()
        out.append(cert_data)

    return out
