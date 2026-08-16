from datetime import date
import uuid

from fastapi import FastAPI, HTTPException
from loguru import logger

from credit_risk.api.schemas import RequestModel, ResponseModel
from credit_risk.modeling.predict import predict_one
from credit_risk.monitoring.prediction_logger import log_predictions

app = FastAPI(title="Credit Risk Default Prediction API")


@app.post("/predict", response_model=ResponseModel)
def predict(request: RequestModel) -> ResponseModel:
    """Runs a the trained and tuned model on one given loan request and returns the request as ResponseModel data model

    Args:
        request (ResponseModel): Loan resquest in ResponseModel type

    Returns:
        ResponseModel: Returns the result of, If the loan is default or not as ResponseModel type
    """
    request_id = str(uuid.uuid4())
    with logger.contextualize(request_id=request_id):
        logger.info("Received prediction request")

        raw_input = request.model_dump()

        try:
            pred, prob, reason_codes = predict_one(raw_input=raw_input)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Inference Failed!: {exc}")

        logger.info(f"Prediction complete: pred={pred}, prob={prob}")

        issue_d = date.today()
        try:
            log_predictions(
                issue_d=issue_d,
                req=request,
                req_id=request_id,
                pred=pred,
                prob=prob,
                reason_codes=reason_codes,
            )
        except Exception as e:
            logger.warning(f"Failed to write prediction log: {e}")

        return ResponseModel(pred=pred, prob=prob, reason_codes=reason_codes)
