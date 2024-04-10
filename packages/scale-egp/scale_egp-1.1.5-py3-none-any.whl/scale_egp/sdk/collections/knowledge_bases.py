from datetime import datetime, timedelta
import json
from typing import List, Optional, Dict, Any, Union

import httpx

from scale_egp.sdk.enums import ChunkUploadStatus
from scale_egp.sdk.enums import EmbeddingModelName, EmbeddingConfigType
from scale_egp.sdk.types.chunks import (
    Chunk,
)
from scale_egp.sdk.types.embeddings import EmbeddingConfigModelsAPI, EmbeddingConfigBase
from scale_egp.sdk.types.knowledge_base_artifacts import (
    KnowledgeBaseArtifact,
    ListKnowledgeBaseArtifactsResponse,
)
from scale_egp.sdk.types.knowledge_base_chunks import (
    KnowledgeBaseChunksResponse,
    KnowledgeBaseQueryRequest,
    KnowledgeBaseQueryResponse,
)
from scale_egp.sdk.types.knowledge_base_uploads import (
    KnowledgeBaseDataSource,
    KnowledgeBaseDataSourceRequest,
    KnowledgeBaseUpload,
    KnowledgeBaseRemoteUploadRequest,
    KnowledgeBaseLocalChunkUploadRequest,
    KnowledgeBaseUploadResponse,
    KnowledgeBaseUploadSchedule,
    KnowledgeBaseUploadSchedulePauseRequest,
    KnowledgeBaseUploadScheduleRequest,
    ListKnowledgeBaseUploadsResponse,
    CancelKnowledgeBaseUploadResponse,
    LocalChunksSourceConfig,
    ChunkingStrategyConfig,
    ChunkToUpload,
    DataSourceAuthConfig,
    RemoteDataSourceConfig,
)
from scale_egp.sdk.types.knowledge_bases import (
    KnowledgeBase,
    KnowledgeBaseRequest,
    KnowledgeBaseResponse,
    ListKnowledgeBasesResponse,
)
from scale_egp.utils.api_utils import APIEngine


class KnowledgeBaseCollection(APIEngine):
    _sub_path = "v2/knowledge-bases"

    def uploads(self) -> "KnowledgeBaseUploadsCollection":
        """
        Returns a KnowledgeBaseUploadsCollection object for uploads associated with a knowledge
        base.

        Returns:
            A KnowledgeBaseUploadsCollection object.
        """
        return KnowledgeBaseUploadsCollection(self._api_client)

    def artifacts(self) -> "KnowledgeBaseArtifactsCollection":
        """
        Returns a KnowledgeBaseArtifactsCollection object for artifacts associated with a
        knowledge base.

        Returns:
            A KnowledgeBaseArtifactsCollection object.
        """
        return KnowledgeBaseArtifactsCollection(self._api_client)

    def chunks(self) -> "KnowledgeBaseChunksCollection":
        """
        Returns a KnowledgeBaseChunksCollection object for chunks associated with a
        knowledge base.

        Returns:
            A KnowledgeBaseChunksCollection object.
        """
        return KnowledgeBaseChunksCollection(self._api_client)
    
    def upload_schedules(self) -> "KnowledgeBaseUploadScheduleCollection":
        """
        Returns a KnowledgeBaseUploadScheduleCollection object for upload schedules associated with a
        knowledge base.

        Returns:
            A KnowledgeBaseUploadScheduleCollection object.
        """
        return KnowledgeBaseUploadScheduleCollection(self._api_client)

    def create(
        self,
        name: str,
        embedding_model_name: Optional[EmbeddingModelName] = None,
        model_deployment_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        account_id: Optional[str] = None,
    ) -> KnowledgeBase:
        """
        Create a new Knowledge Base. Must pass either embedding_model_name or model_deployment_id.

        Args:
            name: The name of the Knowledge Base.
            embedding_model_name: The name of the embedding model to use for the Knowledge Base.
            model_deployment_id: ID for a EmbeddingConfigModelsAPI config.
            metadata: The metadata of the Knowledge Base.
            account_id: The ID of the account to create this Knowledge Base for.

        Returns:
            The newly created Knowledge Base.
        """

        if embedding_model_name is not None and model_deployment_id is not None:
            raise ValueError(
                "Must pass either embedding_model_name or model_deployment_id, not both."
            )
        elif embedding_model_name is not None:
            embedding_config = EmbeddingConfigBase(
                type=EmbeddingConfigType.BASE, embedding_model=embedding_model_name
            )
        elif model_deployment_id is not None:
            embedding_config = EmbeddingConfigModelsAPI(
                type=EmbeddingConfigType.MODELS_API, model_deployment_id=model_deployment_id
            )
        else:
            raise ValueError("Must pass either embedding_model_name or model_deployment_id.")

        response = self._post(
            sub_path=self._sub_path,
            request=KnowledgeBaseRequest(
                account_id=account_id or self._api_client.account_id,
                knowledge_base_name=name,
                embedding_config=embedding_config,
                metadata=metadata,
            ),
        )
        response_model = KnowledgeBaseResponse.from_dict(response.json())
        return self.get(id=response_model.knowledge_base_id)

    def get(
        self,
        id: str,
    ) -> KnowledgeBase:
        """
        Get an Knowledge Base by ID.

        Args:
            id: The ID of the Knowledge Base.

        Returns:
            The Knowledge Base.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return KnowledgeBase.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete a Knowledge Base by ID.

        Args:
            id: The ID of the Knowledge Base.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok

    def list(
        self,
    ) -> List[KnowledgeBase]:
        """
        List all Knowledge Bases.

        Returns:
            A list of Knowledge Bases.
        """
        response = self._get(
            sub_path=self._sub_path,
        )
        response_model = ListKnowledgeBasesResponse.from_dict(response.json())
        return response_model.items


class KnowledgeBaseArtifactsCollection(APIEngine):
    _sub_path = "v2/knowledge-bases/{knowledge_base_id}/artifacts"

    def get(
        self,
        id: str,
        knowledge_base: KnowledgeBase,
        status_filter: Optional[ChunkUploadStatus] = ChunkUploadStatus.COMPLETED.value,
    ) -> KnowledgeBaseArtifact:
        """
        Get a Knowledge Base Artifact by ID.

        Args:
            id: The ID of the Knowledge Base Artifact.
            knowledge_base: The Knowledge Base the artifact was created for.
            status_filter: Return only artifacts with the given status.

        Returns:
            The Knowledge Base Artifact.
        """
        response = self._get(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/"
            f"{id}",
            query_params=dict(
                status_filter=status_filter,
            ),
        )
        return KnowledgeBaseArtifact.from_dict(response.json())

    def list(
        self,
        knowledge_base: KnowledgeBase,
    ) -> List[KnowledgeBaseArtifact]:
        """
        List all Knowledge Base Artifacts.

        Returns:
            A list of Knowledge Base Artifacts.
        """
        response = self._get(
            sub_path=self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id),
        )
        response_model = ListKnowledgeBaseArtifactsResponse.from_dict(response.json())
        return response_model.artifacts


class KnowledgeBaseUploadsCollection(APIEngine):
    _sub_path = "v2/knowledge-bases/{knowledge_base_id}/uploads"

    def create_remote_upload(
        self,
        knowledge_base: KnowledgeBase,
        data_source_config: RemoteDataSourceConfig,
        data_source_auth_config: Optional[DataSourceAuthConfig],
        chunking_strategy_config: ChunkingStrategyConfig,
    ) -> KnowledgeBaseUpload:
        """
        Create a new remote upload.

        Args:
            knowledge_base: The Knowledge Base to upload data to.
            data_source_config: The data source config.
            data_source_auth_config: The data source auth config.
            chunking_strategy_config: The chunking strategy config.

        Returns:
            The newly created remote upload.
        """
        response = self._post(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}",
            request=KnowledgeBaseRemoteUploadRequest(
                data_source_config=data_source_config,
                data_source_auth_config=data_source_auth_config,
                chunking_strategy_config=chunking_strategy_config,
            ),
        )
        response_model = KnowledgeBaseUploadResponse.from_dict(response.json())
        return self.get(id=response_model.upload_id, knowledge_base=knowledge_base)

    def create_local_upload(
        self,
        knowledge_base: KnowledgeBase,
        data_source_config: LocalChunksSourceConfig,
        chunks: List[ChunkToUpload],
    ) -> KnowledgeBaseUpload:
        """
        Create a new local upload.

        Args:
            knowledge_base: The Knowledge Base to upload data to.
            data_source_config: The data source config.
            chunks: The chunks to upload.

        Returns:
            The newly created local upload.
        """
        response = self._post(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}",
            request=KnowledgeBaseLocalChunkUploadRequest(
                data_source_config=data_source_config,
                chunks=chunks,
            ),
        )
        response_model = KnowledgeBaseUploadResponse.from_dict(response.json())
        return self.get(id=response_model.upload_id, knowledge_base=knowledge_base)

    def get(
        self,
        id: str,
        knowledge_base: KnowledgeBase,
    ) -> KnowledgeBaseUpload:
        """
        Get an Knowledge Base Upload by ID.

        Args:
            id: The ID of the Knowledge Base Upload.
            knowledge_base: The Knowledge Base the upload was created for.

        Returns:
            The Knowledge Base Upload.
        """
        response = self._get(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/"
            f"{id}",
        )
        return KnowledgeBaseUpload.from_dict(response.json())

    def list(
        self,
        knowledge_base: KnowledgeBase,
    ) -> List[KnowledgeBaseUpload]:
        """
        List all Knowledge Base Uploads.

        Returns:
            A list of Knowledge Base Uploads.
        """
        response = self._get(
            sub_path=self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id),
        )

        # TODO: This is a hack. Server side field names should be consolidated.
        json_response = response.json()
        for i in range(len(json_response.get("uploads", []))):
            json_response["uploads"][i]["upload_id"] = json_response["uploads"][i]["id"]
        response_model = ListKnowledgeBaseUploadsResponse.from_dict(json_response)
        return response_model.uploads

    def cancel(
        self,
        knowledge_base: KnowledgeBase,
        id: str,
    ) -> bool:
        """
        Cancel an upload.

        Args:
            knowledge_base: The Knowledge Base the upload was created for.
            id: The ID of the upload to cancel.

        Returns:
            True if the upload was canceled, False otherwise.
        """
        response = self._post(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/"
            f"{id}/cancel",
            request=None,
        )
        response_model = CancelKnowledgeBaseUploadResponse.from_dict(response.json())
        return response_model.canceled


class KnowledgeBaseChunksCollection(APIEngine):
    _sub_path = "v2/knowledge-bases/{knowledge_base_id}"

    def query(
        self,
        knowledge_base: KnowledgeBase,
        query: str,
        top_k: int,
        include_embeddings: bool = False,
        metadata_filters: Optional[Dict[str, Any]] = None,
        use_exact_knn: bool = False,
    ) -> List[Chunk]:
        """
        Query a Knowledge Base.

        Args:
            knowledge_base: The Knowledge Base to query.
            query: The query string.
            top_k: The number of results to return.
            include_embeddings: Whether to include embeddings in the response.
            metadata_filters: The metadata to filter query results by. This approach uses a Faiss
                engine with an HNSW algorithm filtering during the k-NN search, as opposed to
                before or after the k-NN search, which ensures that k results are returned (if
                there are at least k results in total).
            use_exact_knn: Whether or not to use exact_knn search (only with top_k <= 1000)

        Returns:
            The query response.
        """

        if use_exact_knn and top_k > 1000:
            raise ValueError("The maximum number of chunks allowed for exact_knn is 1000.")

        path = f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/query"
        if use_exact_knn:
            path = f"{path}?use_exact_knn=true"

        response = self._post(
            sub_path=path,
            request=KnowledgeBaseQueryRequest(
                query=query,
                top_k=top_k,
                include_embeddings=include_embeddings,
                metadata_filters=metadata_filters,
            ),
            # Bump timeout on the knowledge_bases request:
            #   Reasoning for 360 - we set a default timeout of 300s on the opensearch API request,
            #   so we should set this higher than that, otherwise we risk a scenario in which opensearch succeeds
            #   but our API fails.
            timeout=360,
        )
        response_model = KnowledgeBaseQueryResponse.from_dict(response.json())
        return response_model.chunks

    def get(
        self,
        knowledge_base: KnowledgeBase,
        chunk_id: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Get chunks from a Knowledge Base.

        Args:
            knowledge_base: The Knowledge Base to query.
            chunk_id: The chunk ID to match.
            metadata_filters: The metadata whose values to match.

        Returns:
            A list of Chunks.
        """
        query_params = dict()
        if chunk_id:
            query_params["chunk_id"] = chunk_id
        if metadata_filters:
            query_params["metadata_filters"] = json.dumps(metadata_filters)
        response = self._get(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/chunks",
            query_params=query_params,
        )
        response_model = KnowledgeBaseChunksResponse.from_dict(response.json())
        return response_model.chunks


class KnowledgeBaseDataSourceCollection(APIEngine):
    _sub_path = "v3/knowledge-base-data-sources"

    def create(
        self,
        name: str,
        data_source_config: RemoteDataSourceConfig,
        data_source_auth_config: Optional[DataSourceAuthConfig] = None,
        description: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> KnowledgeBaseDataSource:
        """
        Create a new Knowledge Base Data Source.

        Args:
            name: The name of the data source.
            data_source_config: The data source config.
            data_source_auth_config: The data source auth config.
            description: The description of the data source.
            account_id: The ID of the account to create this data source for.

        Returns:
            The newly created data source.
        """
        response = self._post(
            sub_path=self._sub_path,
            request=KnowledgeBaseDataSourceRequest(
                name=name,
                data_source_config=data_source_config,
                data_source_auth_config=data_source_auth_config,
                description=description,
                account_id=account_id or self._api_client.account_id,
            ),
        )
        return KnowledgeBaseDataSource.from_dict(response.json())

    def get(
        self,
        id: str,
    ) -> KnowledgeBaseDataSource:
        """
        Get a Knowledge Base Data Source by ID.

        Args:
            id: The ID of the Knowledge Base Data Source.

        Returns:
            The Knowledge Base Data Source.
        """
        response = self._get(
            sub_path=f"{self._sub_path}/{id}",
        )
        return KnowledgeBaseDataSource.from_dict(response.json())

    def list(
        self,
        account_id: Optional[str] = None,
    ) -> List[KnowledgeBaseDataSource]:
        """
        List all Knowledge Base Data Sources for the given account.

        Args:
            account_id: The ID of the account to list data sources for. Defaults to the account
                associated with the API client.

        Returns:
            A list of Knowledge Base Data Sources.
        """
        response = self._get(
            sub_path=self._sub_path,
            query_params=dict(account_id=account_id or self._api_client.account_id),
        )

        return [KnowledgeBaseDataSource.from_dict(data_source) for data_source in response.json()]

    def verify(
        self,
        knowledge_base_data_source: KnowledgeBaseDataSource,
    ) -> bool:
        """
        Verifies the data source's auth configuration.

        Args:
            knowledge_base_data_source: The Knowledge Base Data Source entity.

        Returns:
            True if the data source auth config is valid, False otherwise.
        """
        response = self._post(
            sub_path=f"{self._sub_path}/{knowledge_base_data_source.id}/verify",
        )
        return response.status_code == httpx.codes.ok

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        data_source_auth_config: Optional[DataSourceAuthConfig] = None,
    ) -> KnowledgeBaseDataSource:
        """
        Update a Knowledge Base Data Source.

        Args:
            id: The ID of the Knowledge Base Data Source.
            name: The updated name of the data source.
            description: The updated description of the data source.
            data_source_auth_config: The updated data source auth config.

        Returns:
            The updated Knowledge Base Data Source.
        """
        response = self._patch(
            sub_path=f"{self._sub_path}/{id}",
            request=KnowledgeBaseDataSourceRequest.partial(
                name=name,
                description=description,
                data_source_auth_config=data_source_auth_config,
            ),
        )
        return KnowledgeBaseDataSource.from_dict(response.json())

    def delete(
        self,
        id: str,
    ) -> bool:
        """
        Delete a Knowledge Base Data Source.

        Args:
            id: The ID of the Knowledge Base Data Source.
        """
        response = self._delete(
            sub_path=f"{self._sub_path}/{id}",
        )
        return response.status_code == httpx.codes.ok


class KnowledgeBaseUploadScheduleCollection(APIEngine):
    _sub_path = "v3/knowledge-bases/{knowledge_base_id}/upload-schedules"

    def create(
        self,
        knowledge_base: KnowledgeBase,
        knowledge_base_data_source: KnowledgeBaseDataSource,
        chunking_strategy_config: ChunkingStrategyConfig,
        interval: timedelta,
        next_run_at: Optional[datetime] = None,
    ) -> KnowledgeBaseUploadSchedule:
        """
        Create a new Knowledge Base Upload Schedule.

        Args:
            knowledge_base: The Knowledge Base to upload data to.
            knowledge_base_data_source: The Knowledge Base Data Source to use for the upload.
            chunking_strategy_config: The chunking strategy config.
            interval: The interval between uploads.
            next_run_at: The time of the next upload.

        Returns:
            The newly created upload schedule.
        """
        response = self._post(
            sub_path=self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id),
            request=KnowledgeBaseUploadScheduleRequest(
                knowledge_base_data_source_id=knowledge_base_data_source.id,
                chunking_strategy_config=chunking_strategy_config,
                interval=interval.total_seconds(),
                next_run_at=next_run_at.isoformat() if next_run_at else None,
                account_id=knowledge_base_data_source.account_id,
            ),
        )
        return KnowledgeBaseUploadSchedule.from_dict(response.json())

    def get(
        self,
        id: str,
        knowledge_base: KnowledgeBase,
    ) -> KnowledgeBaseUploadSchedule:
        """
        Get an Knowledge Base Upload Schedule by ID.

        Args:
            id: The ID of the Knowledge Base Upload Schedule.
            knowledge_base: The Knowledge Base the upload schedule was created for.

        Returns:
            The Knowledge Base Upload Schedule.
        """
        response = self._get(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/{id}"
        )
        return KnowledgeBaseUploadSchedule.from_dict(response.json())

    def list(
        self,
        knowledge_base: KnowledgeBase,
    ) -> List[KnowledgeBaseUploadSchedule]:
        """
        List all Knowledge Base Upload Schedules for a given Knowledge Base.

        Args:
            knowledge_base: The Knowledge Base to list upload schedules for.

        Returns:
            A list of Knowledge Base Upload Schedules.
        """
        response = self._get(
            sub_path=self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id),
        )

        return [
            KnowledgeBaseUploadSchedule.from_dict(upload_schedule)
            for upload_schedule in response.json()
        ]

    def update(
        self,
        id: str,
        knowledge_base: KnowledgeBase,
        chunking_strategy_config: Optional[ChunkingStrategyConfig] = None,
        interval: Optional[timedelta] = None,
        next_run_at: Optional[datetime] = None,
    ) -> KnowledgeBaseUploadSchedule:
        """
        Update a Knowledge Base Upload Schedule.

        Args:
            id: The ID of the Knowledge Base Upload Schedule.
            knowledge_base: The Knowledge Base the upload schedule was created for.
            chunking_strategy_config: The updated chunking strategy config.
            interval: The updated interval between uploads.
            next_run_at: The updated time of the next upload (will resume the scheduled uploads if paused).

        Returns:
            The updated Knowledge Base Upload Schedule.
        """
        response = self._patch(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/{id}",
            request=KnowledgeBaseUploadScheduleRequest.partial(
                chunking_strategy_config=chunking_strategy_config,
                interval=interval.total_seconds() if interval else None,
                next_run_at=next_run_at.isoformat() if next_run_at else None,
            ),
        )
        return KnowledgeBaseUploadSchedule.from_dict(response.json())

    def pause(
        self,
        id: str,
        knowledge_base: KnowledgeBase,
    ) -> KnowledgeBaseUploadSchedule:
        """
        Pause a Knowledge Base Upload Schedule.

        Args:
            id: The ID of the Knowledge Base Upload Schedule.
            knowledge_base: The Knowledge Base the upload schedule was created for.

        Returns:
            The updated Knowledge Base Upload Schedule.
        """
        response = self._patch(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/{id}",
            request=KnowledgeBaseUploadSchedulePauseRequest(),
        )
        return KnowledgeBaseUploadSchedule.from_dict(response.json())

    def resume(
        self,
        id: str,
        knowledge_base: KnowledgeBase,
        next_run_at: datetime,
    ) -> KnowledgeBaseUploadSchedule:
        """
        Pause a Knowledge Base Upload Schedule.

        Args:
            id: The ID of the Knowledge Base Upload Schedule.
            knowledge_base: The Knowledge Base the upload schedule was created for.
            next_run_at: The time to run the next upload.

        Returns:
            The updated Knowledge Base Upload Schedule.
        """
        response = self._patch(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/{id}",
            request=KnowledgeBaseUploadScheduleRequest.partial(
                next_run_at=next_run_at.isoformat(),
            ),
        )
        return KnowledgeBaseUploadSchedule.from_dict(response.json())

    def delete(
        self,
        id: str,
        knowledge_base: KnowledgeBase,
    ) -> bool:
        """
        Delete a Knowledge Base Upload Schedule.

        Args:
            id: The ID of the Knowledge Base Upload Schedule.
            knowledge_base: The Knowledge Base the upload schedule was created for.
        """
        response = self._delete(
            sub_path=f"{self._sub_path.format(knowledge_base_id=knowledge_base.knowledge_base_id)}/{id}",
        )
        return response.status_code == httpx.codes.ok
