from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from benchling_api_client.v2.stable.client import Client

from benchling_sdk.helpers.client_helpers import v2_beta_client
from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.services.v2.base_service import BaseService
from benchling_sdk.services.v2.beta.v2_beta_data_frame_service import V2BetaDataFrameService

if TYPE_CHECKING:
    from benchling_sdk.services.v2.beta.v2_beta_aa_sequence_service import V2BetaAaSequenceService
    from benchling_sdk.services.v2.beta.v2_beta_app_service import V2BetaAppService
    from benchling_sdk.services.v2.beta.v2_beta_collaboration_service import V2BetaCollaborationService
    from benchling_sdk.services.v2.beta.v2_beta_entry_service import V2BetaEntryService
    from benchling_sdk.services.v2.beta.v2_beta_folder_service import V2BetaFolderService
    from benchling_sdk.services.v2.beta.v2_beta_project_service import V2BetaProjectService
    from benchling_sdk.services.v2.beta.v2_beta_worklist_service import V2BetaWorklistService


class V2BetaService(BaseService):
    """
    V2-beta.

    Beta endpoints have different stability guidelines than other stable endpoints.

    See https://benchling.com/api/v2-beta/reference
    """

    _aa_sequence_service: Optional[V2BetaAaSequenceService]
    _app_service: Optional[V2BetaAppService]
    _collaboration_service: Optional[V2BetaCollaborationService]
    _data_frame_service: Optional[V2BetaDataFrameService]
    _entry_service: Optional[V2BetaEntryService]
    _folder_service: Optional[V2BetaFolderService]
    _project_service: Optional[V2BetaProjectService]
    _worklist_service: Optional[V2BetaWorklistService]
    _beta_client: Client

    def __init__(self, client: Client, retry_strategy: RetryStrategy = RetryStrategy()):
        """
        Initialize a v2-beta service.

        :param client: Underlying generated Client.
        :param retry_strategy: Retry strategy for failed HTTP calls
        """
        super().__init__(client, retry_strategy)
        self._beta_client = v2_beta_client(self.client)
        self._aa_sequence_service = None
        self._app_service = None
        self._collaboration_service = None
        self._data_frame_service = None
        self._entry_service = None
        self._folder_service = None
        self._project_service = None
        self._worklist_service = None

    @property
    def aa_sequences(self) -> V2BetaAaSequenceService:
        """
        V2-Beta AA Sequences.

        AA Sequences are the working units of cells that make everything run (they help make structures, catalyze
        reactions and allow for signaling - a kind of internal cell communication). On Benchling, these are comprised
        of a string of amino acids and collections of other attributes, such as annotations.

        See https://benchling.com/api/v2-beta/reference#/AA%20Sequences
        """
        if self._aa_sequence_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_aa_sequence_service import V2BetaAaSequenceService

            self._aa_sequence_service = V2BetaAaSequenceService(self._beta_client, self.retry_strategy)
        return self._aa_sequence_service

    @property
    def apps(self) -> V2BetaAppService:
        """
        V2-Beta Apps.

        Create and manage Apps on your tenant.

        https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps
        """
        if self._app_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_app_service import V2BetaAppService

            self._app_service = V2BetaAppService(self._beta_client, self.retry_strategy)
        return self._app_service

    @property
    def collaborations(self) -> V2BetaCollaborationService:
        """
        V2-Beta Collaborations.

        Collaborations represent which user or group has which access policies.

        See https://benchling.com/api/v2-beta/reference?showLA=true#/Collaborations
        """
        if self._collaboration_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_collaboration_service import (
                V2BetaCollaborationService,
            )

            self._collaboration_service = V2BetaCollaborationService(self._beta_client, self.retry_strategy)
        return self._collaboration_service

    @property
    def data_frames(self) -> V2BetaDataFrameService:
        """
        V2-Beta DataFrames.

        DataFrames are Benchling objects that represent tabular data with typed columns and rows of data.

        See https://benchling.com/api/v2-beta/reference#/Data%20Frames
        """
        if self._data_frame_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_data_frame_service import V2BetaDataFrameService

            self._data_frame_service = V2BetaDataFrameService(self._beta_client, self.retry_strategy)
        return self._data_frame_service

    @property
    def entries(self) -> V2BetaEntryService:
        """
        V2-Beta Entries.

        Entries are rich text documents that allow you to capture all of your experimental data in one place.

        https://benchling.com/api/v2-beta/reference#/Entries
        """
        if self._entry_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_entry_service import V2BetaEntryService

            self._entry_service = V2BetaEntryService(self._beta_client, self.retry_strategy)
        return self._entry_service

    @property
    def folders(self) -> V2BetaFolderService:
        """
        V2-Beta Folders.

        Folders are nested within projects to provide additional organization.

        https://benchling.com/api/v2-beta/reference?showLA=true#/Folders
        """
        if self._folder_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_folder_service import V2BetaFolderService

            self._folder_service = V2BetaFolderService(self._beta_client, self.retry_strategy)
        return self._folder_service

    @property
    def projects(self) -> V2BetaProjectService:
        """
        V2-Beta Projects.

        Manage project objects.

        See https://benchling.com/api/v2-beta/reference?#/Projects
        """
        if self._project_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_project_service import V2BetaProjectService

            self._project_service = V2BetaProjectService(self._beta_client, self.retry_strategy)
        return self._project_service

    @property
    def worklists(self) -> V2BetaWorklistService:
        """
        V2-Beta Worklists.

        Worklists are a convenient way to organize items for bulk actions, and are complementary to folders and
        projects.

        See https://benchling.com/api/v2-beta/reference#/Worklists
        """
        if self._worklist_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_worklist_service import V2BetaWorklistService

            self._worklist_service = V2BetaWorklistService(self._beta_client, self.retry_strategy)
        return self._worklist_service
