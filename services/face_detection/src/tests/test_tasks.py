# TODO: Fix this test
# @pytest.mark.asyncio
# async def test_task_status(client: TestClient, storage: StorageService):
#     service_task_copy = service_task.copy()
#
#     with open("tests/test.jpg", "rb") as file:
#         file_key = await storage.upload(
#             file,
#             ".jpg",
#             service_task_copy["s3_region"],
#             service_task_copy["s3_secret_access_key"],
#             service_task_copy["s3_access_key_id"],
#             service_task_copy["s3_host"],
#             service_task_copy["s3_bucket"],
#         )
#
#         service_task_copy["task"]["data_in"] = [file_key]
#
#         compute_response = client.post("/compute", json=service_task_copy)
#         assert compute_response.status_code == 200
#
#         task_status_response = client.get(f"/status/{service_task_copy['task']['id']}")
#
#         found_at_least_once = False
#         number_of_tries = 0
#         while task_status_response.status_code == 200 and number_of_tries < 5:
#             found_at_least_once = True
#             number_of_tries += 1
#             task_status_response = client.get(f"/status/{service_task_copy['task']['id']}")
#
#         assert found_at_least_once and number_of_tries != 5
#
#
# def test_task_status_not_found(client: TestClient):
#     task_status_response = client.get("/status/00000000-0000-0000-0000-000000000000")
#
#     assert task_status_response.status_code == 404
#
#
# @pytest.mark.asyncio
# async def test_compute_queue_full(client: TestClient, storage: StorageService):
#     service_task_copy = service_task.copy()
#
#     with open("tests/test.jpg", "rb") as file:
#         file_key = await storage.upload(
#             file,
#             ".jpg",
#             service_task_copy["s3_region"],
#             service_task_copy["s3_secret_access_key"],
#             service_task_copy["s3_access_key_id"],
#             service_task_copy["s3_host"],
#             service_task_copy["s3_bucket"],
#         )
#
#         service_task_copy["task"]["data_in"] = [file_key]
#
#         compute_response = client.post("/compute", json=service_task_copy)
#         compute_response = client.post("/compute", json=service_task_copy)
#         compute_response = client.post("/compute", json=service_task_copy)
#
#         assert compute_response.status_code == 503
