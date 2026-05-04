"""End-to-end router tests via FastAPI TestClient."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.domain.telemetry import (
    GpsReading,
    ImuReading,
    Nav2Header,
    Nav2Plan,
    Nav2Pose,
    Quaternion,
    Vector3,
)
from app.repositories.telemetry_repository import TelemetryRepository


def test_health(client: TestClient) -> None:
    assert client.get("/").status_code == 200
    assert client.get("/healthz").json() == {"status": "ok"}


def test_telemetry_endpoints_default(client: TestClient) -> None:
    assert client.get("/api/imu_message").json() == {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}
    assert client.get("/api/gps_message").json() == {
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0.0,
    }
    assert client.get("/api/linear_x").json() == {"linear_x": 0.0}
    assert client.get("/api/angular_z").json() == {"angular_z": 0.0}
    assert client.get("/api/armed_status").json() == {"armed": False}
    assert client.get("/api/mode_status").json() == {"mode": "UNKNOWN"}


def test_all_telemetry_returns_snapshot(client: TestClient) -> None:
    response = client.get("/api/all_telemetry")
    assert response.status_code == 200
    body = response.json()
    assert {"imu", "gps", "odom", "linear_x", "angular_z", "armed", "mode", "nav2_plan"} <= set(
        body
    )


def test_telemetry_endpoint_reflects_repository(
    client: TestClient, telemetry_repository: TelemetryRepository
) -> None:
    telemetry_repository.set_imu(ImuReading(yaw=0.7, pitch=0.1, roll=-0.2))
    telemetry_repository.set_gps(GpsReading(latitude=41.0, longitude=29.0, altitude=5.0))

    imu = client.get("/api/imu_message").json()
    assert imu["yaw"] == 0.7
    gps = client.get("/api/gps_message").json()
    assert gps["latitude"] == 41.0


def test_nav2_plan_404_when_empty(client: TestClient) -> None:
    response = client.get("/api/nav2_plan")
    assert response.status_code == 404
    assert response.json()["error"] == "NotFoundError"


def test_nav2_plan_200_when_populated(
    client: TestClient, telemetry_repository: TelemetryRepository
) -> None:
    plan = Nav2Plan(
        header=Nav2Header(frame_id="map"),
        poses=[
            Nav2Pose(
                position=Vector3(x=1, y=2, z=0),
                orientation=Quaternion(),
                header=Nav2Header(frame_id="map"),
            )
        ],
        pose_count=1,
    )
    telemetry_repository.set_nav2_plan(plan)
    response = client.get("/api/nav2_plan")
    assert response.status_code == 200
    assert response.json()["pose_count"] == 1


def test_save_waypoints_round_trip(client: TestClient) -> None:
    response = client.post(
        "/api/save_waypoints",
        json={
            "waypoints": [
                {"latitude": 41.0, "longitude": 29.0},
                {"latitude": 41.1, "longitude": 29.1},
            ],
            "mission_name": "trial",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mission_name"] == "trial"
    assert len(body["waypoints"]) == 2


def test_save_waypoints_uses_default_name(client: TestClient) -> None:
    response = client.post(
        "/api/save_waypoints",
        json={"waypoints": [{"latitude": 0, "longitude": 0}], "mission_name": ""},
    )
    assert response.status_code == 200
    assert response.json()["mission_name"] == "yildizusv_mission"


def test_save_waypoints_validation_422(client: TestClient) -> None:
    response = client.post(
        "/api/save_waypoints",
        json={"waypoints": [{"latitude": 999, "longitude": 0}]},
    )
    assert response.status_code == 422


def test_save_waypoints_empty_list_422(client: TestClient) -> None:
    response = client.post("/api/save_waypoints", json={"waypoints": []})
    assert response.status_code == 422


def test_save_color_code_form(client: TestClient) -> None:
    response = client.post("/api/save_color_code", data={"color_code": "#FF00AA"})
    assert response.status_code == 200
    assert response.json()["color_code"] == "#FF00AA"


def test_save_color_code_invalid_returns_422(client: TestClient) -> None:
    response = client.post("/api/save_color_code", data={"color_code": "not-hex"})
    assert response.status_code == 422


def test_run_mission_missing_script_returns_502(client: TestClient) -> None:
    # Default tmp_settings creates an empty ros_nodes/ — no script files exist.
    response = client.post("/api/run_mission")
    assert response.status_code == 502
    assert response.json()["error"] == "MissionError"


def test_openapi_schema_lists_all_routes(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    expected = {
        "/api/imu_message",
        "/api/gps_message",
        "/api/odometry",
        "/api/linear_x",
        "/api/angular_z",
        "/api/armed_status",
        "/api/mode_status",
        "/api/nav2_plan",
        "/api/all_telemetry",
        "/api/save_waypoints",
        "/api/save_color_code",
        "/api/run_mission",
        "/api/run_mission2",
    }
    assert expected <= set(paths.keys())
