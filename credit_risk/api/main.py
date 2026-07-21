from fastapi import FastAPI, HTTPException
from credit_risk.api.schemas import RequestModel, ResponseModel
from credit_risk.modeling.predict import predict_one


app = FastAPI(title="Credit Risk Default Prediction API")

@app.post("/predict", response_model=ResponseModel)
def predict(request: RequestModel) -> ResponseModel:
    """Runs a the trained and tuned model on one given loan request and returns the request as ResponseModel data model

    Args:
        request (ResponseModel): Loan resquest in ResponseModel type

    Returns:
        ResponseModel: Returns the result of, If the loan is default or not as ResponseModel type
    """
    
    raw_input = request.model_dump()
    
    try:
        pred, prob, reason_codes = predict_one(raw_input=raw_input)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference Failed!: {exc}")
    
    return ResponseModel(
        pred=pred,
        prob=prob,
        reason_codes=reason_codes
    )