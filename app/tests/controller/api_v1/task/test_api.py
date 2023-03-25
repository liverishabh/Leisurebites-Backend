# from datetime import date, timedelta
# from uuid import uuid4
#
# from app.config import config
# from app.main import test_client as client
#
# auth_header = {
#     "X-Auth-Key": config.AUTH_KEY
# }
#
#
# def test_create_task() -> None:
#     """ Test Create Task API """
#     # Happy Flow
#     payload = {
#         "title": str(uuid4())
#     }
#     response = client.post(f"{config.API_V1_PREFIX}/task", json=payload, headers=auth_header)
#     assert response.status_code == 200
#     assert response.json()["successful"] is True
#
#     # Happy Flow
#     payload = {
#         "title": str(uuid4()),
#         "eta": (date.today() + timedelta(days=5)).strftime(config.DATE_FORMAT),
#         "status": "In Progress"
#     }
#     response = client.post(f"{config.API_V1_PREFIX}/task", json=payload, headers=auth_header)
#     assert response.status_code == 200
#     assert response.json()["successful"] is True
#
#     # Invalid ETA Format
#     payload = {
#         "title": str(uuid4()),
#         "eta": (date.today() + timedelta(days=2)).strftime("%d-%m-%Y")
#     }
#     response = client.post(f"{config.API_V1_PREFIX}/task", json=payload, headers=auth_header)
#     assert response.status_code == 422
#     assert response.json()["successful"] is False
#
#
# def test_get_all_tasks() -> None:
#     """ Test Get All Tasks API """
#     response = client.get(f"{config.API_V1_PREFIX}/task/all", headers=auth_header)
#     assert response.status_code == 200
#     assert response.json()["successful"] is True
#
#
# def test_get_task() -> None:
#     """ Test Get Task by ID API """
#     # Happy Flow
#     all_tasks = client.get(f"{config.API_V1_PREFIX}/task/all", headers=auth_header)
#     for task in all_tasks.json()["data"]["tasks"]:
#         response = client.get(f"{config.API_V1_PREFIX}/task?task_id={task['id']}", headers=auth_header)
#         assert response.status_code == 200
#         assert response.json()["successful"] is True
#
#     # Invalid task_id
#     response = client.get(f"{config.API_V1_PREFIX}/task?task_id=0", headers=auth_header)
#     assert response.status_code == 400
#     assert response.json()["successful"] is False
#
#
# def test_update_task_title() -> None:
#     """ Test Update Task API by updating title """
#     # Happy Flow
#     all_tasks = client.get(f"{config.API_V1_PREFIX}/task/all", headers=auth_header)
#     for task in all_tasks.json()["data"]["tasks"]:
#         payload = {
#             "title": str(uuid4())
#         }
#         response = client.put(f"{config.API_V1_PREFIX}/task?task_id={task['id']}", json=payload, headers=auth_header)
#         assert response.status_code == 200
#         assert response.json()["successful"] is True
#
#     # Invalid task_id
#     payload = {
#         "title": str(uuid4())
#     }
#     response = client.put(f"{config.API_V1_PREFIX}/task?task_id=0", json=payload, headers=auth_header)
#     assert response.status_code == 400
#     assert response.json()["successful"] is False
#
#
# def test_update_task_eta() -> None:
#     """ Test Update Task API by updating eta """
#     all_tasks = client.get(f"{config.API_V1_PREFIX}/task/all", headers=auth_header)
#     payload = {
#         "eta": (date.today() + timedelta(days=3)).strftime(config.DATE_FORMAT),
#     }
#     invalid_payload = {
#         "eta": (date.today() + timedelta(days=2)).strftime("%d-%m-%Y")
#     }
#     for task in all_tasks.json()["data"]["tasks"]:
#         # Happy Flow
#         response = client.put(f"{config.API_V1_PREFIX}/task?task_id={task['id']}", json=payload, headers=auth_header)
#         assert response.status_code == 200
#         assert response.json()["successful"] is True
#
#         # Invalid ETA Format
#         response = client.put(f"{config.API_V1_PREFIX}/task?task_id={task['id']}", json=invalid_payload,
#                               headers=auth_header)
#         assert response.status_code == 422
#         assert response.json()["successful"] is False
#
#     # Invalid task_id
#     response = client.put(f"{config.API_V1_PREFIX}/task?task_id=0", json=payload, headers=auth_header)
#     assert response.status_code == 400
#     assert response.json()["successful"] is False
#
#
# def test_update_task_status() -> None:
#     """ Test Update Task API by updating status """
#     all_tasks = client.get(f"{config.API_V1_PREFIX}/task/all", headers=auth_header)
#     payload = {
#         "status": "Complete",
#     }
#     invalid_payload = {
#         "status": "INVALID",
#     }
#     for task in all_tasks.json()["data"]["tasks"]:
#         # Happy Flow
#         response = client.put(f"{config.API_V1_PREFIX}/task?task_id={task['id']}", json=payload, headers=auth_header)
#         assert response.status_code == 200
#         assert response.json()["successful"] is True
#
#         # Invalid Status Value
#         response = client.put(f"{config.API_V1_PREFIX}/task?task_id={task['id']}", json=invalid_payload,
#                               headers=auth_header)
#         assert response.status_code == 422
#         assert response.json()["successful"] is False
#
#     # Invalid task_id
#     response = client.put(f"{config.API_V1_PREFIX}/task?task_id=0", json=payload, headers=auth_header)
#     assert response.status_code == 400
#     assert response.json()["successful"] is False
#
#
# def test_get_all_task_updates() -> None:
#     """ Test Get All Task Updates API """
#     # Happy Flow
#     all_tasks = client.get(f"{config.API_V1_PREFIX}/task/all", headers=auth_header)
#     for task in all_tasks.json()["data"]["tasks"]:
#         response = client.get(f"{config.API_V1_PREFIX}/task/updates?task_id={task['id']}", headers=auth_header)
#         assert response.status_code == 200
#         assert response.json()["successful"] is True
#
#     # Invalid task_id
#     response = client.get(f"{config.API_V1_PREFIX}/task/updates?task_id=0", headers=auth_header)
#     assert response.status_code == 400
#     assert response.json()["successful"] is False
#
#
# def test_delete_task() -> None:
#     """ Test Delete Task API """
#     # Happy Flow
#     all_tasks = client.get(f"{config.API_V1_PREFIX}/task/all", headers=auth_header)
#     for task in all_tasks.json()["data"]["tasks"]:
#         response = client.delete(f"{config.API_V1_PREFIX}/task?task_id={task['id']}", headers=auth_header)
#         assert response.status_code == 200
#         assert response.json()["successful"] is True
#
#     # Invalid task_id
#     response = client.delete(f"{config.API_V1_PREFIX}/task?task_id=0", headers=auth_header)
#     assert response.status_code == 400
#     assert response.json()["successful"] is False
