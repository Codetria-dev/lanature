from app.models import PasswordResetToken


def test_billing_subscription_and_usage_endpoint(client, auth_headers):
    sub_resp = client.get("/api/v1/billing/subscription/me", headers=auth_headers)
    assert sub_resp.status_code == 200
    payload = sub_resp.json()
    assert payload["plan"]["code"] in {"free", "pro"}
    assert payload["status"] in {"trialing", "active"}

    usage_resp = client.get("/api/v1/billing/usage/me", headers=auth_headers)
    assert usage_resp.status_code == 200
    usage = usage_resp.json()
    assert usage["max_pets"] >= 3
    assert usage["max_routines_per_pet"] >= 10


def test_change_plan_cancel_and_reactivate(client, auth_headers):
    change_resp = client.post(
        "/api/v1/billing/subscription/change",
        json={"plan_code": "free"},
        headers=auth_headers,
    )
    assert change_resp.status_code == 200
    assert change_resp.json()["plan"]["code"] == "free"

    cancel_resp = client.post("/api/v1/billing/subscription/cancel", headers=auth_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["cancel_at_period_end"] is True

    reactivate_resp = client.post("/api/v1/billing/subscription/reactivate", headers=auth_headers)
    assert reactivate_resp.status_code == 200
    assert reactivate_resp.json()["cancel_at_period_end"] is False


def test_password_reset_flow(client, db, test_user):
    email = test_user.email
    old_password = "testpass123"
    new_password = "NewStrongPass456"

    req_resp = client.post("/api/v1/auth/request-password-reset", json={"email": email})
    assert req_resp.status_code == 202

    token_entry = db.query(PasswordResetToken).order_by(PasswordResetToken.id.desc()).first()
    assert token_entry is not None
    token = token_entry.token

    reset_resp = client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": new_password})
    assert reset_resp.status_code == 200

    login_old = client.post("/api/v1/auth/login", json={"email": email, "password": old_password})
    assert login_old.status_code == 401

    login_new = client.post("/api/v1/auth/login", json={"email": email, "password": new_password})
    assert login_new.status_code == 200
