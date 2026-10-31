import pytest
from shipping_quote import process_shipments, monitor_container_pressures

# Example test case:
def test_single_ground_shipment():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": False,
            "express_priority": False,
            "packages": [{"weight_kg": 10, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 60.0
    assert result["status"] == "CLEARED"

# TODO: Add test cases to achieve 90-100% on both Line and Branch coverage!

def test_invalid_shipments_not_list():
    with pytest.raises(ValueError):
        process_shipments("not a list", 10.0)


def test_invalid_negative_handling_fee():
    with pytest.raises(ValueError):
        process_shipments([], -5.0)


def test_manifest_not_approved_skipped():
    shipments = [
        {
            "manifest_approved": False,
            "mode": "ground",
            "packages": [{"weight_kg": 10, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 0.0
    assert result["status"] == "NO_CARGO"


def test_air_mode_shipment():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "air",
            "packages": [{"weight_kg": 5, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "CLEARED"


def test_unknown_mode_rejected():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "sea",
            "packages": [{"weight_kg": 5, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "NO_CARGO"


def test_zero_weight_package_rejected():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "packages": [{"weight_kg": 0, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "CLEARED"
    assert result["total_quote"] == 10.0

def test_hazmat_fragile_zeroes_cost():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": True,
            "packages": [{"weight_kg": 10, "is_hazmat": True}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["total_quote"] == 0.0


def test_hazmat_not_fragile_surcharge():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": False,
            "packages": [{"weight_kg": 10, "is_hazmat": True}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["status"] == "CLEARED"


def test_heavy_package_surcharge():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "packages": [{"weight_kg": 40, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "CLEARED"


def test_express_priority_multiplier():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "express_priority": True,
            "packages": [{"weight_kg": 10, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["status"] == "CLEARED"


def test_flagged_review_too_many_rejects():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "packages": [
                {"weight_kg": 0, "is_hazmat": False},
                {"weight_kg": 0, "is_hazmat": False},
                {"weight_kg": 0, "is_hazmat": False},
                {"weight_kg": 0, "is_hazmat": False},
            ]
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "FLAGGED_REVIEW"


def test_monitor_no_data():
    assert monitor_container_pressures([]) == "NO_DATA"


def test_monitor_leak_detected():
    logs = [[13.5, 13.0, 15.0]]
    assert monitor_container_pressures(logs) == "LEAK_DETECTED"


def test_monitor_stable():
    logs = [[15.0, 16.0, 14.5]]
    assert monitor_container_pressures(logs) == "STABLE"