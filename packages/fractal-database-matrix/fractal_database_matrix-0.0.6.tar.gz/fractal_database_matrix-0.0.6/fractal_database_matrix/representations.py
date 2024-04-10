import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Optional, Sequence

from fractal.matrix import MatrixClient
from fractal_database.representations import Representation
from nio import RoomCreateError, RoomPutStateError, RoomVisibility

if TYPE_CHECKING:
    from fractal_database.models import (
        ReplicatedModel,
        ReplicationTarget,
        RepresentationLog,
    )
    from fractal_database_matrix.models import MatrixReplicationTarget

logger = logging.getLogger(__name__)


class MatrixRepresentation(Representation):
    module = __name__
    initial_state = [
        {
            "type": "f.database",
            "content": {},
        }
    ]

    @classmethod
    @property
    def representation_module(cls):
        return f"{cls.module}.{cls.__name__}"

    async def put_state(
        self,
        room_id: str,
        target: "MatrixReplicationTarget",
        state_type: str,
        content: dict[str, Any],
    ) -> None:
        from fractal.cli.controllers.auth import AuthenticatedController

        creds = AuthenticatedController.get_creds()
        if not creds:
            raise Exception("You must be logged in to put state")

        access_token, homeserver_url, _ = creds

        async with MatrixClient(homeserver_url, access_token) as client:
            res = await client.room_put_state(
                room_id,
                state_type,
                content=content,
            )
            if isinstance(res, RoomPutStateError):
                raise Exception(res.message)
            return None

    async def create_room(
        self,
        target: "MatrixReplicationTarget",
        name: str,
        space: bool = False,
        initial_state: Optional[list[dict[str, Any]]] = None,
        public: bool = False,
        invite: Sequence[str] = (),
    ) -> str:
        from fractal.cli.controllers.auth import AuthenticatedController

        if public:
            visibility = RoomVisibility.public
        else:
            visibility = RoomVisibility.private

        creds = AuthenticatedController.get_creds()
        if not creds:
            raise Exception("You must be logged in to create a room")

        access_token, homeserver_url, _ = creds

        # import pdb

        # pdb.set_trace()

        # verify that matrix IDs passed in invite are all lowercase
        if invite:
            if not any([matrix_id.split("@")[1].islower() for matrix_id in invite]):
                raise Exception("Matrix IDs must be lowercase")

        async with MatrixClient(homeserver_url, access_token) as client:
            res = await client.room_create(
                name=name,
                space=space,
                initial_state=initial_state if initial_state else self.initial_state,
                visibility=visibility,
            )
            if isinstance(res, RoomCreateError):
                raise Exception(res.message)

            room_id = res.room_id

            for account in invite:
                await client.invite(account, room_id, admin=True)

            logger.info(
                "Successfully created %s for %s in Matrix: %s"
                % ("Room" if not space else "Space", name, room_id)
            )

        return res.room_id

    async def add_subspace(
        self, target: "MatrixReplicationTarget", parent_room_id: str, child_room_id: str
    ) -> None:
        # fetch the non-base class version of the target so it will contain the Matrix specific properties
        from fractal.cli.controllers.auth import AuthenticatedController

        creds = AuthenticatedController.get_creds()
        if not creds:
            raise Exception("You must be logged in to add a subspace")

        access_token, homeserver_url, _ = creds

        async with MatrixClient(homeserver_url, access_token) as client:
            res = await client.room_put_state(
                parent_room_id,
                "m.space.child",
                {"via": [target.homeserver]},
                state_key=child_room_id,
            )
            if isinstance(res, RoomPutStateError):
                raise Exception(res.message)

            logger.info(
                "Successfully added child space %s to parent space %s"
                % (child_room_id, parent_room_id)
            )


class MatrixRoom(MatrixRepresentation):
    async def create_representation(
        self, repr_log: "RepresentationLog", target_id: Any
    ) -> dict[str, str]:
        """
        Creates a Matrix room for the ReplicatedModel "instance" that inherits from this class
        """
        try:
            name = repr_log.metadata["name"]
            public = repr_log.metadata.get("public", False)
        except KeyError:
            raise Exception("name must be specified in metadata")

        target: "MatrixReplicationTarget" = (
            await repr_log.target_type.model_class()
            .objects.select_related("database")
            .prefetch_related("database__devices", "matrixcredentials_set", "instances")
            .aget(pk=repr_log.target_id)
        )  # type: ignore

        matrix_ids_to_invite = [target.matrix_id for target in target.matrixcredentials_set.all()]
        room_id = await self.create_room(
            target=target,
            name=name,
            space=False,
            public=public,
            invite=matrix_ids_to_invite,
        )

        # accept invites to room
        for account in target.matrixcredentials_set.all():
            await account.accept_invite(room_id, target)

        logger.info("Successfully created Matrix Room representation for %s" % name)
        return {"room_id": room_id}


class MatrixSpace(MatrixRepresentation):
    initial_state = [
        {
            "type": "f.database",
            "content": {},
        },
        {"type": "f.database.target", "content": {}},
    ]

    async def create_representation(
        self, repr_log: "RepresentationLog", target_id: Any
    ) -> dict[str, str]:
        """
        Creates a Matrix space for the ReplicatedModel "instance" that inherits from this class
        """
        try:
            name = repr_log.metadata["name"]
        except KeyError:
            raise Exception("name must be specified in metadata")

        target: "MatrixReplicationTarget" = (
            await repr_log.target_type.model_class()
            .objects.select_related("database")
            .prefetch_related("database__devices", "matrixcredentials_set", "instances")
            .aget(pk=repr_log.target_id)
        )  # type: ignore

        logger.info(
            "Creating Matrix space for %s on target %s" % (repr_log.metadata["name"], target)
        )

        matrix_ids_to_invite = [cred.matrix_id for cred in target.matrixcredentials_set.all()]
        initial_state = deepcopy(self.initial_state)
        room_id = await self.create_room(
            target=target,
            name=name,
            space=True,
            initial_state=initial_state,
            invite=matrix_ids_to_invite,
        )

        devices_room_id = await self.create_room(
            target=target,
            name="Devices",
            space=True,
            initial_state=initial_state,
            invite=matrix_ids_to_invite,
        )

        for account in target.matrixcredentials_set.all():
            # accept invites to rooms
            await account.accept_invite(room_id, target)
            await account.accept_invite(devices_room_id, target)

        await self.add_subspace(target, room_id, devices_room_id)

        target.metadata["room_id"] = room_id
        target.metadata["devices_room_id"] = room_id

        if target.database:
            initial_state[0]["content"]["fixture"] = await target.database.ato_fixture(
                json=True, with_relations=True
            )
        initial_state[1]["content"]["fixture"] = await target.ato_fixture(
            json=True, with_relations=True
        )

        await self.put_state(room_id, target, "f.database", initial_state[0]["content"])
        await self.put_state(room_id, target, "f.database.target", initial_state[1]["content"])

        logger.info(
            "Successfully created Matrix Space representation for %s on target %s"
            % (name, target)
        )
        return {"room_id": room_id, "devices_room_id": devices_room_id}


class MatrixSubSpace(MatrixSpace):
    @classmethod
    def create_representation_logs(
        cls,
        instance: "ReplicatedModel",
        target: "ReplicationTarget",
    ):
        """
        Create the representation logs (tasks) for creating a Matrix subspace
        """
        from fractal_database.models import RepresentationLog

        # create the representation logs for the subspace
        create_subspace = MatrixSpace.create_representation_logs(instance, target)

        # create the representation log for adding the subspace to the parent space
        add_subspace_to_parent = RepresentationLog.objects.create(
            instance=instance,
            method=cls.representation_module,
            target=target,
            metadata=instance.repr_metadata_props(),
        )
        create_subspace.append(add_subspace_to_parent)
        return create_subspace

    async def create_representation(self, repr_log: "RepresentationLog", target_id: Any) -> None:
        """
        Creates a Matrix space for the ReplicatedModel "instance" that inherits from this class
        """
        # get the model the object that this representation log is for
        # (this is usually a ReplicationTarget model since only ReplicationTargets can create representations)
        model_class: "MatrixReplicationTarget" = repr_log.content_type.model_class()  # type: ignore
        # get the model for the target that this representation log is for
        target_model = repr_log.target_type.model_class()
        # fetch the replicated model that this representation log is for
        instance = await model_class.objects.aget(pk=repr_log.object_id)
        # fetch the target
        target: "MatrixReplicationTarget" = await target_model.objects.prefetch_related(
            "matrixcredentials_set"
        ).aget(
            pk=target_id
        )  # type: ignore

        # pull room ids from metadata
        parent_room_id = target.metadata["room_id"]
        child_room_id = instance.metadata["room_id"]
        if parent_room_id == child_room_id:
            raise Exception("Parent and child room IDs cannot be the same")

        await self.add_subspace(target, parent_room_id, child_room_id)


class MatrixSubRoom(MatrixSubSpace):
    @classmethod
    def create_representation_logs(
        cls,
        instance: "ReplicatedModel",
        target: "ReplicationTarget",
    ):
        """
        Create the representation logs (tasks) for creating a Matrix subroom
        (A room that is in a space.)
        """
        from fractal_database.models import RepresentationLog

        # create the representation logs for the subspace
        create_subroom = MatrixRoom.create_representation_logs(instance, target)

        # create the representation log for adding the subspace to the parent space
        add_subroom_to_parent = RepresentationLog.objects.create(
            instance=instance,
            method=cls.representation_module,
            target=target,
            metadata=instance.repr_metadata_props(),
        )
        create_subroom.append(add_subroom_to_parent)
        return create_subroom


class MatrixExistingSubSpace(MatrixSubSpace):
    @classmethod
    def create_representation_logs(
        cls,
        instance: "ReplicatedModel",
        target: "ReplicationTarget",
    ):
        """
        Create the representation logs (tasks) for creating a Matrix space
        """
        from fractal_database.models import RepresentationLog

        # create the representation log for adding the subspace to the parent space
        add_subspace_to_parent = RepresentationLog.objects.create(
            instance=instance,
            method=cls.representation_module,
            target=target,
            metadata=instance.repr_metadata_props(),
        )
        return [add_subspace_to_parent]


class AppSpace(MatrixSpace):
    initial_state = [
        {
            "type": "f.database.app",
            "content": {},
        }
    ]
