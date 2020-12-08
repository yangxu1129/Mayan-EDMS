from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.testing.tests.base import GenericViewTestCase

from ..models import Workflow
from ..permissions import (
    permission_workflow_create, permission_workflow_delete,
    permission_workflow_edit, permission_workflow_view,
    permission_workflow_tools
)

from .literals import TEST_WORKFLOW_LABEL, TEST_WORKFLOW_LABEL_EDITED
from .mixins import (
    DocumentWorkflowTemplateViewTestMixin, WorkflowTestMixin,
    WorkflowToolViewTestMixin, WorkflowViewTestMixin
)


class DocumentWorkflowTemplateViewTestCase(
    DocumentWorkflowTemplateViewTestMixin, WorkflowTestMixin,
    GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self.test_workflow.document_types.add(self.test_document_type)
        self.test_workflow.auto_launch = False
        self.test_workflow.save()

    def test_document_single_workflow_launch_view_no_permission(self):
        self._upload_test_document()
        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_test_document_single_workflow_launch_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )

    def test_document_single_workflow_launch_view_with_document_access(self):
        self._upload_test_document()
        self.grant_access(
            obj=self.test_document, permission=permission_workflow_tools
        )

        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_test_document_single_workflow_launch_view()
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )

    def test_document_single_workflow_launch_view_with_workflow_access(self):
        self._upload_test_document()
        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_tools
        )

        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_test_document_single_workflow_launch_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )

    def test_document_single_workflow_launch_view_with_full_access(self):
        self._upload_test_document()
        self.grant_access(
            obj=self.test_document, permission=permission_workflow_tools
        )
        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_tools
        )

        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_test_document_single_workflow_launch_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count + 1
        )

    def test_trashed_document_single_workflow_launch_view_with_full_access(self):
        self._upload_test_document()
        self.grant_access(
            obj=self.test_document, permission=permission_workflow_tools
        )
        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_tools
        )

        workflow_instance_count = self.test_document.workflows.count()

        self.test_document.delete()

        response = self._request_test_document_single_workflow_launch_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )


class WorkflowViewTestCase(
    WorkflowTestMixin, WorkflowViewTestMixin, GenericViewTestCase
):
    def test_workflow_create_view_no_permission(self):
        response = self._request_test_workflow_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(Workflow.objects.count(), 0)

    def test_workflow_create_view_with_permission(self):
        self.grant_permission(permission=permission_workflow_create)

        response = self._request_test_workflow_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Workflow.objects.count(), 1)
        self.assertEqual(Workflow.objects.all()[0].label, TEST_WORKFLOW_LABEL)

    def test_workflow_delete_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(self.test_workflow in Workflow.objects.all())

    def test_workflow_delete_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_delete
        )

        response = self._request_test_workflow_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertFalse(self.test_workflow in Workflow.objects.all())

    def test_workflow_edit_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.label, TEST_WORKFLOW_LABEL)

    def test_workflow_edit_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_workflow.refresh_from_db()
        self.assertEqual(self.test_workflow.label, TEST_WORKFLOW_LABEL_EDITED)

    def test_workflow_list_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_list_view()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, text=self.test_workflow.label)

    def test_workflow_list_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_list_view()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text=self.test_workflow.label)

    def test_workflow_template_preview_view_no_permission(self):
        self._create_test_workflow()

        response = self._request_test_workflow_template_preview_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(self.test_workflow in Workflow.objects.all())

    def test_workflow_template_preview_view_with_access(self):
        self._create_test_workflow()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )
        response = self._request_test_workflow_template_preview_view()
        self.assertEqual(response.status_code, 200)


class WorkflowTemplateDocumentViewTestCase(
    WorkflowTestMixin, WorkflowViewTestMixin, GenericDocumentViewTestCase
):
    def test_workflows_launch_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_test_workflow_launch_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )

    def test_workflows_launch_view_with_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_tools
        )

        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_test_workflow_launch_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count + 1
        )

    def test_trashed_document_workflows_launch_view_with_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_tools
        )

        workflow_instance_count = self.test_document.workflows.count()

        self.test_document.delete()

        response = self._request_test_workflow_launch_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )


class WorkflowToolViewTestCase(
    WorkflowTestMixin, WorkflowToolViewTestMixin, GenericDocumentViewTestCase
):
    def test_tool_launch_workflows_view_no_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_workflow_launch_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )

    def test_tool_launch_workflows_view_with_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_permission(permission=permission_workflow_tools)

        workflow_instance_count = self.test_document.workflows.count()

        response = self._request_workflow_launch_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count + 1
        )

    def test_trashed_document_tool_launch_workflows_view_with_permission(self):
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_permission(permission=permission_workflow_tools)

        workflow_instance_count = self.test_document.workflows.count()

        self.test_document.delete()

        response = self._request_workflow_launch_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_document.workflows.count(), workflow_instance_count
        )
