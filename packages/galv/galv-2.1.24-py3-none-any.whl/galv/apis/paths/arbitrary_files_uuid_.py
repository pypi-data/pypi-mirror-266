from galv.paths.arbitrary_files_uuid_.get import ApiForget
from galv.paths.arbitrary_files_uuid_.delete import ApiFordelete
from galv.paths.arbitrary_files_uuid_.patch import ApiForpatch


class ArbitraryFilesUuid(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
