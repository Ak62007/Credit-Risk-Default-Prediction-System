from fastapi.testclient import TestClient
from credit_risk.api.main import app

client = TestClient(app=app)

def test_predict_valid_request(raw_input):
    json_input = {
        **raw_input,
        "earliest_cr_line": raw_input['earliest_cr_line'].isoformat()
    }
    response = client.post(
        '/predict',
        json=json_input
    )
    
    assert response.status_code == 200
    body = response.json()
    assert body['pred'] in [0, 1]
    assert 0 <= body['prob'] <= 1
    assert len(body['reason_codes']) == 5
    
def test_predict_missing_required_field(raw_input):
    bad_input = {
        **raw_input,
        "earliest_cr_line": raw_input['earliest_cr_line'].isoformat()
    }
    
    bad_input.pop('annual_inc')
    
    response = client.post('/predict', json=bad_input)

    assert response.status_code == 422
    detail = response.json()['detail']
    assert any('annual_inc' in error['loc'] for error in detail), (
        "The 422 error isn't about the missing 'annual_inc' field."
    )

def test_predict_wrong_type_field(raw_input):
    wrong_type = {
        **raw_input,
        "earliest_cr_line": raw_input['earliest_cr_line'].isoformat(),
        'annual_inc': 'not a number'
    }
    
    response = client.post('/predict', json=wrong_type)

    assert response.status_code == 422
    detail = response.json()['detail']
    assert any('annual_inc' in error['loc'] for error in detail), (
        "The 422 error isn't about the wrong-typed 'annual_inc' field."
    )

def test_predict_null_optional_field(raw_input):
    good_input = {
        **raw_input,
        "earliest_cr_line": raw_input['earliest_cr_line'].isoformat(),
        'mths_since_last_delinq': None
    }
    
    response = client.post('/predict', json=good_input)
    
    assert response.status_code == 200
    