import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from ark_sdk_python.models.common import ArkStatus
from ark_sdk_python.models.services.cmgr.ark_cmgr_component import (
    ArkCmgrComponent,
    ArkCmgrComponentStatusCode,
    MaintenanceOperationDetails,
    MaintenanceOperationStatus,
)
from ark_sdk_python.models.services.cmgr.ark_cmgr_component_operation_async_task import ArkCmgrComponentOperationAsyncTask
from ark_sdk_python.models.services.cmgr.ark_cmgr_uninstall_component import ArkCmgrUninstallComponent
from ark_sdk_python.services.cmgr.ark_cmgr_component_operation_async_request import ArkCmgrComponentOperationAsyncRequest


def _make_component(
    maintenance_status: MaintenanceOperationStatus,
    component_status: ArkCmgrComponentStatusCode,
) -> ArkCmgrComponent:
    details = MaintenanceOperationDetails.model_construct(status=maintenance_status, progress=0.0)
    return ArkCmgrComponent.model_construct(
        component_id="comp-1",
        connector_id="conn-1",
        component_status=component_status,
        maintenance_operation_details=details,
    )


def _make_task(
    maintenance_status: MaintenanceOperationStatus,
    component_status: ArkCmgrComponentStatusCode,
    operation: str = "UNINSTALL",
) -> ArkCmgrComponentOperationAsyncTask:
    component = _make_component(maintenance_status, component_status)
    return ArkCmgrComponentOperationAsyncTask.model_construct(
        task_id="comp-1",
        component=component,
        operation=operation,
    )


class TestArkCmgrComponentOperationAsyncTaskUninstall(unittest.TestCase):
    def test_uninstall_component_deleted_returns_success(self) -> None:
        # component_deleted=True is the only success path for uninstall
        task = _make_task(MaintenanceOperationStatus.SUCCEEDED, ArkCmgrComponentStatusCode.ACTIVE)
        task.component_deleted = True
        self.assertEqual(task.task_status(), ArkStatus.Success)

    def test_uninstall_succeeded_but_component_still_visible_returns_in_progress(
        self,
    ) -> None:
        # SUCCEEDED + component still present → keep polling
        task = _make_task(MaintenanceOperationStatus.SUCCEEDED, ArkCmgrComponentStatusCode.ACTIVE)
        self.assertEqual(task.task_status(), ArkStatus.InProgress)

    def test_uninstall_failed_returns_failed(self) -> None:
        task = _make_task(MaintenanceOperationStatus.FAILED, ArkCmgrComponentStatusCode.ACTIVE)
        self.assertEqual(task.task_status(), ArkStatus.Failed)

    def test_install_succeeded_active_returns_success(self) -> None:
        task = _make_task(
            MaintenanceOperationStatus.SUCCEEDED,
            ArkCmgrComponentStatusCode.ACTIVE,
            operation="INSTALL",
        )
        self.assertEqual(task.task_status(), ArkStatus.Success)

    def test_install_succeeded_non_active_returns_failed(self) -> None:
        task = _make_task(
            MaintenanceOperationStatus.SUCCEEDED,
            ArkCmgrComponentStatusCode.SUSPENDED,
            operation="INSTALL",
        )
        self.assertEqual(task.task_status(), ArkStatus.Failed)


class TestArkCmgrServiceUninstall(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_isp_auth = MagicMock()
        self.patches = [
            patch("ark_sdk_python.services.cmgr.ark_cmgr_service.ArkISPServiceClient"),
            patch(
                "ark_sdk_python.services.cmgr.ark_cmgr_service.ArkService.__init__",
                return_value=None,
            ),
        ]
        for patcher in self.patches:
            patcher.start()

        from ark_sdk_python.services.cmgr.ark_cmgr_service import ArkCmgrService

        self.service = ArkCmgrService(self.mock_isp_auth)
        self.mock_client = MagicMock()
        self.service._ArkCmgrService__client = self.mock_client  # pylint: disable=protected-access
        self.service._logger = MagicMock()  # pylint: disable=protected-access

    def tearDown(self) -> None:
        for patcher in self.patches:
            patcher.stop()

    def _accepted_response(self) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.status_code = HTTPStatus.ACCEPTED
        return mock_resp

    def _real_component(self) -> ArkCmgrComponent:
        return _make_component(MaintenanceOperationStatus.RUNNING, ArkCmgrComponentStatusCode.ACTIVE)

    def test_uninstall_component_returns_async_request(self) -> None:
        self.mock_client.post.return_value = self._accepted_response()
        with patch.object(self.service, "connector_component", return_value=self._real_component()):
            req = self.service.uninstall_component(ArkCmgrUninstallComponent(connector_id="conn-1", component_id="comp-1"))
        self.assertIsInstance(req, ArkCmgrComponentOperationAsyncRequest)

    def test_uninstall_component_task_has_uninstall_operation(self) -> None:
        self.mock_client.post.return_value = self._accepted_response()
        with patch.object(self.service, "connector_component", return_value=self._real_component()):
            req = self.service.uninstall_component(ArkCmgrUninstallComponent(connector_id="conn-1", component_id="comp-1"))
        self.assertEqual(req.async_task.operation, "UNINSTALL")

    def test_uninstall_component_raises_on_non_accepted(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = HTTPStatus.BAD_REQUEST
        mock_resp.text = "bad request"
        self.mock_client.post.return_value = mock_resp

        from ark_sdk_python.models import ArkServiceException

        with self.assertRaises(ArkServiceException):
            self.service.uninstall_component(ArkCmgrUninstallComponent(connector_id="conn-1", component_id="comp-1"))

    def test_uninstall_component_passes_extra_vars(self) -> None:
        self.mock_client.post.return_value = self._accepted_response()
        with patch.object(self.service, "connector_component", return_value=self._real_component()):
            self.service.uninstall_component(
                ArkCmgrUninstallComponent(
                    connector_id="conn-1",
                    component_id="comp-1",
                    extra_vars={"key": "value"},
                )
            )
        call_kwargs = self.mock_client.post.call_args[1]
        self.assertEqual(call_kwargs["json"], {"extra_vars": {"key": "value"}})

    def test_uninstall_component_no_extra_vars_sends_empty_dict(self) -> None:
        self.mock_client.post.return_value = self._accepted_response()
        with patch.object(self.service, "connector_component", return_value=self._real_component()):
            self.service.uninstall_component(ArkCmgrUninstallComponent(connector_id="conn-1", component_id="comp-1"))
        call_kwargs = self.mock_client.post.call_args[1]
        self.assertEqual(call_kwargs["json"], {"extra_vars": {}})

    def test_uninstall_connector_calls_winrm_uninstall(self) -> None:
        mock_connector = MagicMock()
        mock_connector.connector_host_ip = "1.2.3.4"
        with (
            patch.object(self.service, "connector", return_value=mock_connector),
            patch.object(
                self.service, "_ArkCmgrService__uninstall_connector_on_machine"
            ) as mock_uninstall,  # pylint: disable=protected-access
        ):
            from ark_sdk_python.models.services.cmgr.ark_cmgr_uninstall_connector import ArkCmgrUninstallConnector

            self.service.uninstall_connector(ArkCmgrUninstallConnector(connector_id="conn-1", username="admin"))
            mock_uninstall.assert_called_once()


if __name__ == "__main__":
    unittest.main()
