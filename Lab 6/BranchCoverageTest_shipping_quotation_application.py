import pytest
from shipping_quote import process_shipments, monitor_container_pressures


def test_hazmat_not_fragile_heavy_weight():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "is_fragile": False,
            "packages": [{"weight_kg": 40, "is_hazmat": True}]
        }
    ]
    result = process_shipments(shipments, 20.0)
    assert result["status"] == "CLEARED"


def test_monitor_streak_resets_on_stable_reading():
    logs = [[13.0, 15.0, 13.5]]
    assert monitor_container_pressures(logs) == "STABLE"


def test_express_priority_with_heavy_weight():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "air",
            "express_priority": True,
            "packages": [{"weight_kg": 35, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 15.0)
    assert result["status"] == "CLEARED"
    assert result["total_quote"] == round((15.0 + 35 * (12.0 * 1.5)) * 1.25, 2)


def test_multiple_shipments_mixed_results():
    shipments = [
        {
            "manifest_approved": True,
            "mode": "ground",
            "packages": [{"weight_kg": 10, "is_hazmat": False}]
        },
        {
            "manifest_approved": False,
            "mode": "air",
            "packages": [{"weight_kg": 20, "is_hazmat": False}]
        },
        {
            "manifest_approved": True,
            "mode": "sea",
            "packages": [{"weight_kg": 5, "is_hazmat": False}]
        }
    ]
    result = process_shipments(shipments, 10.0)
    assert result["status"] == "CLEARED"