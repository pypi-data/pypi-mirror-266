from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from benchling_api_client.v2.stable.client import Client

from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.services.v2.base_service import BaseService

if TYPE_CHECKING:
    from benchling_sdk.services.v2.stable.aa_sequence_service import AaSequenceService
    from benchling_sdk.services.v2.stable.api_service import ApiService
    from benchling_sdk.services.v2.stable.app_service import AppService
    from benchling_sdk.services.v2.stable.assay_result_service import AssayResultService
    from benchling_sdk.services.v2.stable.assay_run_service import AssayRunService
    from benchling_sdk.services.v2.stable.blob_service import BlobService
    from benchling_sdk.services.v2.stable.box_service import BoxService
    from benchling_sdk.services.v2.stable.container_service import ContainerService
    from benchling_sdk.services.v2.stable.custom_entity_service import CustomEntityService
    from benchling_sdk.services.v2.stable.custom_notation_service import CustomNotationService
    from benchling_sdk.services.v2.stable.dna_alignments_service import DnaAlignmentsService
    from benchling_sdk.services.v2.stable.dna_oligo_service import DnaOligoService
    from benchling_sdk.services.v2.stable.dna_sequence_service import DnaSequenceService
    from benchling_sdk.services.v2.stable.dropdown_service import DropdownService
    from benchling_sdk.services.v2.stable.entity_service import EntityService
    from benchling_sdk.services.v2.stable.entry_service import EntryService
    from benchling_sdk.services.v2.stable.event_service import EventService
    from benchling_sdk.services.v2.stable.export_service import ExportService
    from benchling_sdk.services.v2.stable.feature_library_service import FeatureLibraryService
    from benchling_sdk.services.v2.stable.folder_service import FolderService
    from benchling_sdk.services.v2.stable.inventory_service import InventoryService
    from benchling_sdk.services.v2.stable.lab_automation_service import LabAutomationService
    from benchling_sdk.services.v2.stable.label_template_service import LabelTemplateService
    from benchling_sdk.services.v2.stable.location_service import LocationService
    from benchling_sdk.services.v2.stable.mixture_service import MixtureService
    from benchling_sdk.services.v2.stable.molecule_service import MoleculeService
    from benchling_sdk.services.v2.stable.nucleotide_alignments_service import NucleotideAlignmentsService
    from benchling_sdk.services.v2.stable.oligo_service import OligoService
    from benchling_sdk.services.v2.stable.organization_service import OrganizationService
    from benchling_sdk.services.v2.stable.plate_service import PlateService
    from benchling_sdk.services.v2.stable.printer_service import PrinterService
    from benchling_sdk.services.v2.stable.project_service import ProjectService
    from benchling_sdk.services.v2.stable.registry_service import RegistryService
    from benchling_sdk.services.v2.stable.request_service import RequestService
    from benchling_sdk.services.v2.stable.rna_oligo_service import RnaOligoService
    from benchling_sdk.services.v2.stable.rna_sequence_service import RnaSequenceService
    from benchling_sdk.services.v2.stable.schema_service import SchemaService
    from benchling_sdk.services.v2.stable.task_service import TaskService
    from benchling_sdk.services.v2.stable.team_service import TeamService
    from benchling_sdk.services.v2.stable.user_service import UserService
    from benchling_sdk.services.v2.stable.warehouse_service import WarehouseService
    from benchling_sdk.services.v2.stable.workflow_output_service import WorkflowOutputService
    from benchling_sdk.services.v2.stable.workflow_task_group_service import WorkflowTaskGroupService
    from benchling_sdk.services.v2.stable.workflow_task_service import WorkflowTaskService


class V2StableService(BaseService):
    """
    V2 Stable.

    Namespace containing support for the V2 stable endpoints of the Benchling API.
    """

    _aa_sequence_service: Optional[AaSequenceService]
    _api_service: Optional[ApiService]
    _app_service: Optional[AppService]
    _assay_result_service: Optional[AssayResultService]
    _assay_run_service: Optional[AssayRunService]
    _blob_service: Optional[BlobService]
    _box_service: Optional[BoxService]
    _container_service: Optional[ContainerService]
    _custom_entity_service: Optional[CustomEntityService]
    _custom_notation_service: Optional[CustomNotationService]
    _dropdown_service: Optional[DropdownService]
    _dna_alignments_service: Optional[DnaAlignmentsService]
    _dna_oligo_service: Optional[DnaOligoService]
    _dna_sequence_service: Optional[DnaSequenceService]
    _entities_service: Optional[EntityService]
    _entries_service: Optional[EntryService]
    _event_service: Optional[EventService]
    _export_service: Optional[ExportService]
    _feature_library_service: Optional[FeatureLibraryService]
    _folder_service: Optional[FolderService]
    _inventory_service: Optional[InventoryService]
    _lab_automation_service: Optional[LabAutomationService]
    _label_templates_service: Optional[LabelTemplateService]
    _location_service: Optional[LocationService]
    _mixture_service: Optional[MixtureService]
    _molecule_service: Optional[MoleculeService]
    _nucleotide_alignments: Optional[NucleotideAlignmentsService]
    _oligo_service: Optional[OligoService]
    _organization_service: Optional[OrganizationService]
    _plate_service: Optional[PlateService]
    _printer_service: Optional[PrinterService]
    _project_service: Optional[ProjectService]
    _registry_service: Optional[RegistryService]
    _request_service: Optional[RequestService]
    _rna_oligo_service: Optional[RnaOligoService]
    _rna_sequence_service: Optional[RnaSequenceService]
    _schema_service: Optional[SchemaService]
    _task_service: Optional[TaskService]
    _team_service: Optional[TeamService]
    _user_service: Optional[UserService]
    _warehouse_service: Optional[WarehouseService]
    _workflow_output_service: Optional[WorkflowOutputService]
    _workflow_task_group_service: Optional[WorkflowTaskGroupService]
    _workflow_task_service: Optional[WorkflowTaskService]

    def __init__(self, client: Client, retry_strategy: RetryStrategy = RetryStrategy()):
        """
        Initialize a service.

        :param client: Underlying generated Client.
        :param retry_strategy: Retry strategy for failed HTTP calls
        """
        super().__init__(client, retry_strategy)
        self._aa_sequence_service = None
        self._api_service = None
        self._app_service = None
        self._assay_result_service = None
        self._assay_run_service = None
        self._blob_service = None
        self._box_service = None
        self._container_service = None
        self._custom_entity_service = None
        self._custom_notation_service = None
        self._dropdown_service = None
        self._dna_alignments_service = None
        self._dna_oligo_service = None
        self._dna_sequence_service = None
        self._entities_service = None
        self._entries_service = None
        self._event_service = None
        self._export_service = None
        self._feature_library_service = None
        self._folder_service = None
        self._inventory_service = None
        self._lab_automation_service = None
        self._label_templates_service = None
        self._location_service = None
        self._mixture_service = None
        self._molecule_service = None
        self._nucleotide_alignments = None
        self._oligo_service = None
        self._organization_service = None
        self._plate_service = None
        self._printer_service = None
        self._project_service = None
        self._registry_service = None
        self._request_service = None
        self._rna_oligo_service = None
        self._rna_sequence_service = None
        self._schema_service = None
        self._task_service = None
        self._team_service = None
        self._user_service = None
        self._warehouse_service = None
        self._workflow_output_service = None
        self._workflow_task_group_service = None
        self._workflow_task_service = None

    @property
    def aa_sequences(self) -> AaSequenceService:
        """
        AA Sequences.

        AA Sequences are the working units of cells that make everything run (they help make structures, catalyze
        reactions and allow for signaling - a kind of internal cell communication). On Benchling, these are comprised
        of a string of amino acids and collections of other attributes, such as annotations.

        See https://benchling.com/api/reference#/AA%20Sequences
        """
        if self._aa_sequence_service is None:
            from benchling_sdk.services.v2.stable.aa_sequence_service import AaSequenceService

            self._aa_sequence_service = AaSequenceService(self._client, retry_strategy=self._retry_strategy)
        return self._aa_sequence_service

    @property
    def api(self) -> ApiService:
        """
        Make custom API calls with the underlying BenchlingApiClient.

        A common use case for this is making calls to API endpoints which may not yet be supported in the current SDK
        release. It's capable of making more "generic" calls utilizing our authorization scheme, as well as supporting
        some simple serialization and deserialization for custom models.
        """
        if self._api_service is None:
            from benchling_sdk.services.v2.stable.api_service import ApiService

            self._api_service = ApiService(self._client, retry_strategy=self._retry_strategy)
        return self._api_service

    @property
    def apps(self) -> AppService:
        """
        Apps.

        Apps provide a framework for you to customize your teams’ experiences on
        Benchling with custom applications.

        See https://benchling.com/api/reference#/Apps
        and https://docs.benchling.com/docs/getting-started-benchling-apps
        """
        if self._app_service is None:
            from benchling_sdk.services.v2.stable.app_service import AppService

            self._app_service = AppService(self._client, retry_strategy=self._retry_strategy)
        return self._app_service

    @property
    def assay_results(self) -> AssayResultService:
        """
        Assay Results.

        Results represent the output of assays that have been performed. You can customize the schemas of results to
        fit your needs. Results can link to runs, batches, and other types.

        See https://benchling.com/api/reference#/Assay%20Results
        """
        if self._assay_result_service is None:
            from benchling_sdk.services.v2.stable.assay_result_service import AssayResultService

            self._assay_result_service = AssayResultService(self._client, retry_strategy=self._retry_strategy)
        return self._assay_result_service

    @property
    def assay_runs(self) -> AssayRunService:
        """
        Assay Runs.

        Runs capture the details / parameters of a run that was performed. Results are usually nested under a run.

        See https://benchling.com/api/reference#/Assay%20Runs
        """
        if self._assay_run_service is None:
            from benchling_sdk.services.v2.stable.assay_run_service import AssayRunService

            self._assay_run_service = AssayRunService(self._client, retry_strategy=self._retry_strategy)
        return self._assay_run_service

    @property
    def blobs(self) -> BlobService:
        """
        Blobs.

        Blobs are opaque files that can be linked to other items in Benchling, like assay runs or results. For example,
        you can upload a blob, then upload an assay result that links to that blob by ID. The blob will then appear as
        part of the assay result in the Benchling web UI.

        See https://benchling.com/api/reference#/Blobs
        """
        if self._blob_service is None:
            from benchling_sdk.services.v2.stable.blob_service import BlobService

            self._blob_service = BlobService(self._client, retry_strategy=self._retry_strategy)
        return self._blob_service

    @property
    def boxes(self) -> BoxService:
        """
        Boxes.

        Boxes are a structured storage type, consisting of a grid of positions that can each hold one container. Unlike
        locations, there are a maximum number of containers that a box can hold (one per position).

        Boxes are all associated with schemas, which define the type of the box (e.g. "10x10 Cryo Box") along with the
        fields that are tracked and the dimensions of the box.

        Like all storage, every Box has a barcode that is unique across the registry.

        See https://benchling.com/api/reference#/Boxes
        """
        if self._box_service is None:
            from benchling_sdk.services.v2.stable.box_service import BoxService

            self._box_service = BoxService(self._client, retry_strategy=self._retry_strategy)
        return self._box_service

    @property
    def containers(self) -> ContainerService:
        """
        Containers.

        Containers are the backbone of sample management in Benchling. They represent physical containers, such as
        tubes or wells, that hold quantities of biological samples (represented by the batches inside the container).
        The container itself tracks its total volume, and the concentration of every batch inside of it.

        Containers are all associated with schemas, which define the type of the container (e.g. "Tube") along with the
        fields that are tracked.

        Like all storage, every container has a barcode that is unique across the registry.

        See https://benchling.com/api/reference#/Containers
        """
        if self._container_service is None:
            from benchling_sdk.services.v2.stable.container_service import ContainerService

            self._container_service = ContainerService(self._client, retry_strategy=self._retry_strategy)
        return self._container_service

    @property
    def custom_entities(self) -> CustomEntityService:
        """
        Custom Entities.

        Benchling supports custom entities for biological entities that are neither sequences or proteins. Custom
        entities must have an entity schema set and can have both schema fields and custom fields.

        See https://benchling.com/api/reference#/Custom%20Entities
        """
        if self._custom_entity_service is None:
            from benchling_sdk.services.v2.stable.custom_entity_service import CustomEntityService

            self._custom_entity_service = CustomEntityService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._custom_entity_service

    @property
    def custom_notations(self) -> CustomNotationService:
        """
        Custom Notations.

        Benchling allows users to configure their own fully-custom string representation formats for import/export
        of nucleotide sequences (including chemical modifications).

        See https://benchling.com/api/reference#/Custom%20Notations
        """
        if self._custom_notation_service is None:
            from benchling_sdk.services.v2.stable.custom_notation_service import CustomNotationService

            self._custom_notation_service = CustomNotationService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._custom_notation_service

    @property
    def dna_alignments(self) -> DnaAlignmentsService:
        """
        DNA Alignments.

        A DNA alignment is a Benchling object representing an alignment of multiple DNA sequences.

        See https://benchling.com/api/reference#/DNA%20Alignments
        """
        if self._dna_alignments_service is None:
            from benchling_sdk.services.v2.stable.dna_alignments_service import DnaAlignmentsService

            self._dna_alignments_service = DnaAlignmentsService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._dna_alignments_service

    @property
    def dna_oligos(self) -> DnaOligoService:
        """
        DNA Oligos.

        DNA Oligos are short linear DNA sequences that can be attached as primers to full DNA sequences. Just like other
        entities, they support schemas, tags, and aliases.

        See https://benchling.com/api/reference#/DNA%20Oligos
        """
        if self._dna_oligo_service is None:
            from benchling_sdk.services.v2.stable.dna_oligo_service import DnaOligoService

            self._dna_oligo_service = DnaOligoService(self._client, retry_strategy=self._retry_strategy)
        return self._dna_oligo_service

    @property
    def dna_sequences(self) -> DnaSequenceService:
        """
        DNA Sequences.

        DNA sequences are the bread and butter of the Benchling Molecular Biology suite. On Benchling, these are
        comprised of a string of nucleotides and collections of other attributes, such as annotations and primers.

        See https://benchling.com/api/reference#/DNA%20Sequences
        """
        if self._dna_sequence_service is None:
            from benchling_sdk.services.v2.stable.dna_sequence_service import DnaSequenceService

            self._dna_sequence_service = DnaSequenceService(self._client, retry_strategy=self._retry_strategy)
        return self._dna_sequence_service

    @property
    def rna_sequences(self) -> RnaSequenceService:
        """
        RNA Sequences.

        Chains of linear, single stranded RNA that support most capabilities and attributes of DNA Sequences.

        See https://benchling.com/api/reference#/RNA%20Sequences
        """
        if self._rna_sequence_service is None:
            from benchling_sdk.services.v2.stable.rna_sequence_service import RnaSequenceService

            self._rna_sequence_service = RnaSequenceService(self._client, retry_strategy=self._retry_strategy)
        return self._rna_sequence_service

    @property
    def dropdowns(self) -> DropdownService:
        """
        Dropdowns.

        Dropdowns are registry-wide enums. Use dropdowns to standardize on spelling and naming conventions, especially
        for important metadata like resistance markers.

        See https://benchling.com/api/reference#/Dropdowns
        """
        if self._dropdown_service is None:
            from benchling_sdk.services.v2.stable.dropdown_service import DropdownService

            self._dropdown_service = DropdownService(self._client, retry_strategy=self._retry_strategy)
        return self._dropdown_service

    @property
    def entities(self) -> EntityService:
        """
        Entities.

        Entities include DNA and AA sequences, oligos, molecules, custom entities, and
        other biological objects in Benchling. Entities support schemas, tags, and aliases,
        and can be registered.

        See https://benchling.com/api/reference#/Entities
        """
        if self._entities_service is None:
            from benchling_sdk.services.v2.stable.entity_service import EntityService

            self._entities_service = EntityService(self._client, retry_strategy=self._retry_strategy)
        return self._entities_service

    @property
    def entries(self) -> EntryService:
        """
        Entries.

        Entries are rich text documents that allow you to capture all of your experimental data in one place.

        See https://benchling.com/api/reference#/Entries
        """
        if self._entries_service is None:
            from benchling_sdk.services.v2.stable.entry_service import EntryService

            self._entries_service = EntryService(self._client, retry_strategy=self._retry_strategy)
        return self._entries_service

    @property
    def events(self) -> EventService:
        """
        Events.

        The Events system allows external services to subscribe to events that are triggered in Benchling (e.g. plasmid
        registration, request submission, etc).

        See https://benchling.com/api/reference#/Events
        """
        if self._event_service is None:
            from benchling_sdk.services.v2.stable.event_service import EventService

            self._event_service = EventService(self._client, retry_strategy=self._retry_strategy)
        return self._event_service

    @property
    def exports(self) -> ExportService:
        """
        Exports.

        Export a Notebook Entry.

        See https://benchling.com/api/reference#/Exports
        """
        if self._export_service is None:
            from benchling_sdk.services.v2.stable.export_service import ExportService

            self._export_service = ExportService(self._client, retry_strategy=self._retry_strategy)
        return self._export_service

    @property
    def feature_libraries(self) -> FeatureLibraryService:
        """
        Feature Libraries.

        Feature Libraries are collections of shared canonical patterns that can be used to generate
        annotations on matching regions of DNA Sequences or AA Sequences.

        See https://benchling.com/api/reference#/Feature%20Libraries
        """
        if self._feature_library_service is None:
            from benchling_sdk.services.v2.stable.feature_library_service import FeatureLibraryService

            self._feature_library_service = FeatureLibraryService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._feature_library_service

    @property
    def folders(self) -> FolderService:
        """
        Folders.

        Manage folder objects.

        See https://benchling.com/api/reference#/Folders
        """
        if self._folder_service is None:
            from benchling_sdk.services.v2.stable.folder_service import FolderService

            self._folder_service = FolderService(self._client, retry_strategy=self._retry_strategy)
        return self._folder_service

    @property
    def inventory(self) -> InventoryService:
        """
        Inventory.

        Manage inventory wide objects.

        See https://benchling.com/api/reference#/Inventory
        """
        if self._inventory_service is None:
            from benchling_sdk.services.v2.stable.inventory_service import InventoryService

            self._inventory_service = InventoryService(self._client, retry_strategy=self._retry_strategy)
        return self._inventory_service

    @property
    def lab_automation(self) -> LabAutomationService:
        """
        Lab Automation.

        Lab Automation endpoints support integration with lab instruments, and liquid handlers to create samples or
        results, and capture transfers between containers at scale.

        See https://benchling.com/api/reference#/Lab%20Automation
        """
        if self._lab_automation_service is None:
            from benchling_sdk.services.v2.stable.lab_automation_service import LabAutomationService

            self._lab_automation_service = LabAutomationService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._lab_automation_service

    @property
    def label_templates(self) -> LabelTemplateService:
        """
        Label Templates.

        List label templates.

        See https://benchling.com/api/reference#/Label%20Templates
        """
        if self._label_templates_service is None:
            from benchling_sdk.services.v2.stable.label_template_service import LabelTemplateService

            self._label_templates_service = LabelTemplateService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._label_templates_service

    @property
    def locations(self) -> LocationService:
        """
        Locations.

        Manage locations objects. Like all storage, every Location has a barcode that is unique across the registry.

        See https://benchling.com/api/reference#/Locations
        """
        if self._location_service is None:
            from benchling_sdk.services.v2.stable.location_service import LocationService

            self._location_service = LocationService(self._client, retry_strategy=self._retry_strategy)
        return self._location_service

    @property
    def mixtures(self) -> MixtureService:
        """
        Mixtures.

        Mixtures are solutions comprised of multiple ingredients where the exact quantities of each ingredient are
        important to track. Each ingredient is uniquely identified by its component entity.

        See https://benchling.com/api/reference#/Mixtures
        """
        if self._mixture_service is None:
            from benchling_sdk.services.v2.stable.mixture_service import MixtureService

            self._mixture_service = MixtureService(self._client, retry_strategy=self._retry_strategy)
        return self._mixture_service

    @property
    def molecules(self) -> MoleculeService:
        """
        Molecules.

        Molecules are groups of atoms held together by bonds, representing entities smaller than DNA
        Sequences and AA Sequences. Just like other entities, they support schemas, tags, and aliases.

        See https://benchling.com/api/reference#/Molecules
        """
        if self._molecule_service is None:
            from benchling_sdk.services.v2.stable.molecule_service import MoleculeService

            self._molecule_service = MoleculeService(self._client, retry_strategy=self._retry_strategy)
        return self._molecule_service

    @property
    def nucleotide_alignments(self) -> NucleotideAlignmentsService:
        """
        Nucleotide Alignments.

        A Nucleotide Alignment is a Benchling object representing an alignment of multiple DNA and/or RNA sequences.

        See https://benchling.com/api/reference#/Nucleotide%20Alignments
        """
        if self._nucleotide_alignments is None:
            from benchling_sdk.services.v2.stable.nucleotide_alignments_service import (
                NucleotideAlignmentsService,
            )

            self._nucleotide_alignments = NucleotideAlignmentsService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._nucleotide_alignments

    @property
    def oligos(self) -> OligoService:
        """
        Oligos.

        Oligos are short linear DNA sequences that can be attached as primers to full DNA sequences. Just like other
        entities, they support schemas, tags, and aliases.

        Please migrate to the corresponding DNA Oligos endpoints so that we can support RNA Oligos.

        See https://benchling.com/api/reference#/Oligos
        """
        if self._oligo_service is None:
            from benchling_sdk.services.v2.stable.oligo_service import OligoService

            self._oligo_service = OligoService(self._client, retry_strategy=self._retry_strategy)
        return self._oligo_service

    @property
    def organizations(self) -> OrganizationService:
        """
        Organizations.

        View organization objects.

        See https://benchling.com/api/reference#/Organizations
        """
        if self._organization_service is None:
            from benchling_sdk.services.v2.stable.organization_service import OrganizationService

            self._organization_service = OrganizationService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._organization_service

    @property
    def plates(self) -> PlateService:
        """
        Plates.

        Plates are a structured storage type, grids of wells that each function like containers. Plates come in two
        types: a traditional "fixed" type, where the wells cannot move, and a "matrix" type. A matrix plate has similar
        functionality to a box, where the containers inside can be moved around and removed altogether.

        Plates are all associated with schemas, which define the type of the plate (e.g. "96 Well Plate") along with
        the fields that are tracked, the dimensions of the plate, and whether or not the plate is a matrix plate or a
        traditional well plate.

        Like all storage, every Plate has a barcode that is unique across the registry.

        See https://benchling.com/api/reference#/Plates
        """
        if self._plate_service is None:
            from benchling_sdk.services.v2.stable.plate_service import PlateService

            self._plate_service = PlateService(self._client, retry_strategy=self._retry_strategy)
        return self._plate_service

    @property
    def printers(self) -> PrinterService:
        """
        Printers.

        List printers.

        See https://benchling.com/api/reference#/Printers
        """
        if self._printer_service is None:
            from benchling_sdk.services.v2.stable.printer_service import PrinterService

            self._printer_service = PrinterService(self._client, retry_strategy=self._retry_strategy)
        return self._printer_service

    @property
    def projects(self) -> ProjectService:
        """
        Projects.

        Manage project objects.

        See https://benchling.com/api/reference#/Projects
        """
        if self._project_service is None:
            from benchling_sdk.services.v2.stable.project_service import ProjectService

            self._project_service = ProjectService(self._client, retry_strategy=self._retry_strategy)
        return self._project_service

    @property
    def registry(self) -> RegistryService:
        """
        Registry.

        Manage registry objects.

        See https://benchling.com/api/reference#/Registry
        """
        if self._registry_service is None:
            from benchling_sdk.services.v2.stable.registry_service import RegistryService

            self._registry_service = RegistryService(self._client, retry_strategy=self._retry_strategy)
        return self._registry_service

    @property
    def requests(self) -> RequestService:
        """
        Requests.

        Requests allow scientists and teams to collaborate around experimental assays and workflows.

        See https://benchling.com/api/reference#/Requests
        """
        if self._request_service is None:
            from benchling_sdk.services.v2.stable.request_service import RequestService

            self._request_service = RequestService(self._client, retry_strategy=self._retry_strategy)
        return self._request_service

    @property
    def rna_oligos(self) -> RnaOligoService:
        """
        RNA Oligos.

        RNA Oligos are short linear RNA sequences that can be attached as primers to full DNA sequences. Just like other
        entities, they support schemas, tags, and aliases.

        See https://benchling.com/api/reference#/RNA%20Oligos
        """
        if self._rna_oligo_service is None:
            from benchling_sdk.services.v2.stable.rna_oligo_service import RnaOligoService

            self._rna_oligo_service = RnaOligoService(self._client, retry_strategy=self._retry_strategy)
        return self._rna_oligo_service

    @property
    def schemas(self) -> SchemaService:
        """
        Schemas.

        Schemas represent custom configuration of objects in Benchling. See https://docs.benchling.com/docs/schemas in
        our documentation on how Schemas impact our developers

        See https://benchling.com/api/reference#/Schemas
        """
        if self._schema_service is None:
            from benchling_sdk.services.v2.stable.schema_service import SchemaService

            self._schema_service = SchemaService(self._client, retry_strategy=self._retry_strategy)
        return self._schema_service

    @property
    def tasks(self) -> TaskService:
        """
        Tasks.

        Endpoints that perform expensive computations launch long-running tasks. These endpoints return the task ID (a
        UUID) in the response body.

        After launching a task, periodically invoke the Get a task endpoint with the task UUID (e.g., every 10
        seconds), until the status is no longer RUNNING.

        You can access a task for up to 30 minutes after its completion, after which its data will no longer be
        available.

        See https://benchling.com/api/reference#/Tasks
        """
        if self._task_service is None:
            from benchling_sdk.services.v2.stable.task_service import TaskService

            self._task_service = TaskService(self._client, retry_strategy=self._retry_strategy)
        return self._task_service

    @property
    def teams(self) -> TeamService:
        """
        Teams.

        View team objects.

        See https://benchling.com/api/reference#/Teams
        """
        if self._team_service is None:
            from benchling_sdk.services.v2.stable.team_service import TeamService

            self._team_service = TeamService(self._client, retry_strategy=self._retry_strategy)
        return self._team_service

    @property
    def users(self) -> UserService:
        """
        Benchling users.

        See https://benchling.com/api/reference#/Users
        """
        if self._user_service is None:
            from benchling_sdk.services.v2.stable.user_service import UserService

            self._user_service = UserService(self._client, retry_strategy=self._retry_strategy)
        return self._user_service

    @property
    def warehouse(self) -> WarehouseService:
        """
        Warehouse.

        Manage warehouse credentials.

        See https://benchling.com/api/reference#/Warehouse
        """
        if self._warehouse_service is None:
            from benchling_sdk.services.v2.stable.warehouse_service import WarehouseService

            self._warehouse_service = WarehouseService(self._client, retry_strategy=self._retry_strategy)
        return self._warehouse_service

    @property
    def workflow_outputs(self) -> WorkflowOutputService:
        """
        Workflow Outputs.

        Workflow outputs are outputs of a workflow task.

        See https://benchling.com/api/reference#/Workflow%20Outputs
        """
        if self._workflow_output_service is None:
            from benchling_sdk.services.v2.stable.workflow_output_service import WorkflowOutputService

            self._workflow_output_service = WorkflowOutputService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._workflow_output_service

    @property
    def workflow_task_groups(self) -> WorkflowTaskGroupService:
        """
        Workflow Tasks Groups.

        Workflow task groups are groups of workflow tasks of the same schema.

        See https://benchling.com/api/reference#/Workflow%20Task%20Groups
        """
        if self._workflow_task_group_service is None:
            from benchling_sdk.services.v2.stable.workflow_task_group_service import WorkflowTaskGroupService

            self._workflow_task_group_service = WorkflowTaskGroupService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._workflow_task_group_service

    @property
    def workflow_tasks(self) -> WorkflowTaskService:
        """
        Workflow Tasks.

        Workflow tasks encapsulate a single unit of work.

        See https://benchling.com/api/reference#/Workflow%20Tasks
        """
        if self._workflow_task_service is None:
            from benchling_sdk.services.v2.stable.workflow_task_service import WorkflowTaskService

            self._workflow_task_service = WorkflowTaskService(
                self._client, retry_strategy=self._retry_strategy
            )
        return self._workflow_task_service
