from credit_risk.modeling.predict import predict_one, threshold

def test_output_structure(raw_input):

    pred, prob, reason_codes = predict_one(raw_input=raw_input)
    
    assert pred in [0, 1], (
        f"Function: {predict_one.__name__}: The predictions should be either 0 or 1."
    )
    assert prob >= 0 and prob <= 1, (
        f"Function: {predict_one.__name__}: The prediction probability value is invalid it should be between 0 and 1."
    )
    assert len(reason_codes) == 5, (
        f"Function: {predict_one.__name__}: It is returning more than 5 reason codes."
    )
    assert sorted(reason_codes.values(), key=abs, reverse=True) == list(reason_codes.values()), (
        f"Function: {predict_one.__name__}: The values of the reason codes are not sorted correctly!"
    )
    
def test_handles_earliest_cr_line_as_date(raw_input):
    """Regression test for the datetime.date vs pd.Timestamp TypeError hit during M15.

    request.model_dump() hands predict_one a real datetime.date for
    earliest_cr_line, not a string. This confirms predict_one still handles
    that type correctly rather than relying on it silently working the way
    a string input would.
    """
    pred, prob, reason_codes = predict_one(raw_input=raw_input)

    assert isinstance(pred, int), (
        f"Function: {predict_one.__name__}: didn't return a valid prediction when given a real date object."
    )
    assert isinstance(prob, float), (
        f"Function: {predict_one.__name__}: didn't return a valid probability when given a real date object."
    )
    assert isinstance(reason_codes, dict), (
        f"Function: {predict_one.__name__}: didn't return valid reason codes when given a real date object."
    )    

def test_threshold_check(raw_input):
    pred, prob, _ = predict_one(raw_input=raw_input)
    
    ans = None
    if prob >= threshold:
        ans = 1
    else:
        ans = 0
    assert ans == pred, (
        f"Function: {predict_one.__name__}: The threshold checking is not correctly done!"
    )

def _assert_valid_output(pred, prob, reason_codes):
    assert pred in [0, 1], (
        f"Function: {predict_one.__name__}: The predictions should be either 0 or 1."
    )
    assert prob >= 0 and prob <= 1, (
        f"Function: {predict_one.__name__}: The prediction probability value is invalid it should be between 0 and 1."
    )
    assert len(reason_codes) == 5, (
        f"Function: {predict_one.__name__}: It is returning more than 5 reason codes."
    )
    
def test_handles_null_optional_fields(raw_input):
    """Regression test: predict_one must still work when the nullable fields
    are explicitly None, not just when they're omitted."""
    
    nullable_input = {
        **raw_input,
        "mths_since_last_delinq": None,
        "mths_since_last_record": None,
        "mths_since_last_major_derog": None,
        "mths_since_recent_bc": None,
        "mths_since_recent_bc_dlq": None,
        "mths_since_recent_inq": None,
        "mths_since_recent_revol_delinq": None,
    }
    
    pred, prob, reason_codes = predict_one(nullable_input)
    
    _assert_valid_output(pred=pred, prob=prob, reason_codes=reason_codes)
    
def test_high_risk_profile_scores_higher(low_risk_input, high_risk_input):
    
    _, low_risk_prob, _ = predict_one(raw_input=low_risk_input)
    _, high_risk_prob, _ = predict_one(raw_input=high_risk_input)
    
    assert low_risk_prob < high_risk_prob, (
        f"Function: {predict_one.__name__}: high-risk profile ({high_risk_prob}) "
        f"did not score higher than the low-risk profile ({low_risk_prob})."
    )