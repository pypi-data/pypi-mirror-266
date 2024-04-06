import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import pytz
from twisted.internet.task import LoopingCall

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.TupleActionVortex import TupleActionVortex
from vortex.TupleSelector import TupleSelector
from vortex.data_loader.TupleDataLoaderTupleABC import TupleDataLoaderTupleABC
from vortex.data_loader.TupleDataLoaderTuples import (
    _LockDataTupleAction,
    _DataLockStatusTuple,
)
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class _DataLockStatusTupleSelector:
    """Data lock status Tuple Selector

    This class provides some consistency on how the data lock status
    tuple selector is structured.
    """

    DATA_TUPLE_SELECTOR_KEY = "dataTupleSelector"

    @classmethod
    def getDataTupleSelector(
        cls, tupleSelector: TupleSelector
    ) -> TupleSelector:
        assert tupleSelector.name == _DataLockStatusTuple.tupleType(), (
            "_DataLockStatusTupleSelector"
            " tupleSelector.name is not _DataLockStatusTuple.tupleType()"
        )
        return tupleSelector.selector[cls.DATA_TUPLE_SELECTOR_KEY]

    @classmethod
    def makeLockTupleSelector(
        cls, dataTupleSelector: TupleSelector
    ) -> TupleSelector:
        return TupleSelector(
            name=_DataLockStatusTuple.tupleType(),
            selector={
                _DataLockStatusTupleSelector.DATA_TUPLE_SELECTOR_KEY: dataTupleSelector
            },
        )


class _LockState:
    LOCK_EXPIRE = timedelta(hours=2)

    def __init__(
        self,
        tupleDataSelector: TupleSelector,
    ):
        self.tupleDataSelector = tupleDataSelector

        self._locked = False
        self.lockedByDelegateUuid = None
        self.lockStart = None
        self.lockedByUserUuid: Optional[str] = None
        self.lockedByVortexUuid: Optional[str] = None

        self.lockTouched = datetime.now(pytz.UTC)
        self.liveUpdateDataFromDelegateUuid: Optional[str] = None
        self.liveUpdateDataTuple: Optional[TupleDataLoaderTupleABC] = None

        self.unlockedByDelegateUuid = None
        self.lockDeleted = False
        self.lockDeletedFromDelegateUuid: Optional[str] = None

    def lock(
        self,
        delegateUuid: str,
        lockedByUserUuid: str,
        lockedByVortexUuid: str,
    ):
        assert not self.deleted, (
            "_LockState: An attempt to lock a deleted lock. "
            + self.tupleDataSelector.toJsonStr()
        )
        self._locked = True
        self._lockedByDelegateUuid = delegateUuid
        self.lockedByUserUuid: Optional[str] = lockedByUserUuid
        self.lockedByVortexUuid: Optional[str] = lockedByVortexUuid

        self.lockStart = datetime.now(pytz.UTC)
        self.lockTouched = datetime.now(pytz.UTC)
        self.unlockedByDelegateUuid = None

    def touch(self, delegateUuid: str, liveUpdateData: TupleDataLoaderTupleABC):
        assert not self.deleted, (
            "_LockState: An attempt to touch a deleted lock. "
            + self.tupleDataSelector.toJsonStr()
        )
        assert self._locked, (
            "_LockState: An attempt to touch a non-locked lock. "
            + self.tupleDataSelector.toJsonStr()
        )
        self.lockTouched = datetime.now(pytz.UTC)
        self.liveUpdateDataFromDelegateUuid = delegateUuid
        self.liveUpdateDataTuple = liveUpdateData

    def delete(self, delegateUuid: str):
        assert not self.deleted, (
            "_LockState: An attempt to delete a deleted lock. "
            + self.tupleDataSelector.toJsonStr()
        )
        self.lockDeleted = True
        self.lockDeletedFromDelegateUuid = delegateUuid

        self._locked = False
        self.lockTouched = datetime.now(pytz.UTC)

        self.liveUpdateDataTuple = None
        self.liveUpdateDataFromDelegateUuid = None

    def unlock(self, delegateUuid: str):
        assert not self.deleted, (
            "_LockState: An attempt to unlock a deleted lock. "
            + self.tupleDataSelector.toJsonStr()
        )
        assert self._locked, (
            "_LockState: An attempt to unlock a non-locked lock. "
            + self.tupleDataSelector.toJsonStr()
        )
        self._locked = False
        self.lockTouched = datetime.now(pytz.UTC)
        self.unlockedByDelegateUuid = delegateUuid

        self.liveUpdateDataTuple = None
        self.lockDeletedFromDelegateUuid = None

    @property
    def expired(self) -> bool:
        return (self.lockTouched + self.LOCK_EXPIRE) < datetime.now(pytz.UTC)

    @property
    def deleted(self) -> bool:
        return self.lockDeleted

    @property
    def locked(self) -> bool:
        return self._locked

    @property
    def autoExpireDate(self) -> datetime:
        return self.lockTouched + self.LOCK_EXPIRE


class TupleDataLiveLockManager:
    LOCK_CHECK_SECONDS = 5

    def __init__(self):
        self._lockStateByDataSelectorByDataTupleType: dict[
            str, [str, _LockState]
        ] = defaultdict(dict)
        self._lockExpiredLoopingCall = LoopingCall(self._checkLockExpired)
        self._observer: Optional[TupleDataObservableHandler] = None

    def start(self, observer: TupleDataObservableHandler):
        self._observer = observer
        self._lockExpiredLoopingCall.start(self.LOCK_CHECK_SECONDS)

    def shutdown(self):
        self._observer = None
        self._lockExpiredLoopingCall.stop()
        self._lockExpiredLoopingCall = None

    def _checkLockExpired(self):
        for (
            tupleDataType,
            lockStateByDataSelector,
        ) in list(self._lockStateByDataSelectorByDataTupleType.items()):
            for (
                tupleSelectorStr,
                lockState,
            ) in list(lockStateByDataSelector.items()):
                if not lockState.expired:
                    continue

                logger.info("Unlocking. Lock expired for %s", tupleSelectorStr)
                if lockState.locked:
                    self.unlock(
                        lockState.tupleDataSelector, "_checkLockExpired"
                    )
                else:
                    lockStateByDataSelector.pop(tupleSelectorStr, None)

    def _lock(
        self,
        tupleAction: _LockDataTupleAction,
        tupleActionVortex: TupleActionVortex,
    ) -> None:
        tupleDataSelector: TupleSelector = tupleAction.tupleDataSelector
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lockStateByDataSelector = self._lockStateByDataSelectorByDataTupleType[
            tupleDataType
        ]
        lockState = lockStateByDataSelector.get(
            tupleSelectorStr,
            _LockState(
                tupleDataSelector=tupleDataSelector,
            ),
        )

        assert (
            not lockState.locked
            or lockState.lockedByUserUuid == tupleAction.userUuid
        ), (
            "TupleDataLiveLockManager: We received a lock action from a user"
            " that does not have the lock. " + tupleSelectorStr
        )

        assert tupleAction.liveUpdateDataTuple, (
            "TupleDataLiveLockManager: We received an empty"
            " tupleAction.liveUpdateDataTuple. " + tupleSelectorStr
        )

        assert not lockState.deleted, (
            "TupleDataLiveLockManager: We received an request to lock"
            " but the data has been deleted. " + tupleSelectorStr
        )

        if not lockState.locked:
            lockState.lock(
                lockedByUserUuid=tupleAction.userUuid,
                lockedByVortexUuid=tupleActionVortex.uuid,
                delegateUuid=tupleAction.delegateUuid,
            )

        lockState.touch(
            tupleAction.delegateUuid, tupleAction.liveUpdateDataTuple
        )
        lockStateByDataSelector[tupleSelectorStr] = lockState

        self._observer.notifyOfTupleUpdate(
            _DataLockStatusTupleSelector.makeLockTupleSelector(
                lockState.tupleDataSelector
            )
        )

    def hasLock(self, tupleDataSelector: TupleSelector, userUuid: str) -> bool:
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lock = self._lockStateByDataSelectorByDataTupleType[tupleDataType].get(
            tupleSelectorStr
        )

        return lock and lock.locked and lock.lockedByUserUuid == userUuid

    def isLocked(self, tupleDataSelector: TupleSelector) -> bool:
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lock = self._lockStateByDataSelectorByDataTupleType[tupleDataType].get(
            tupleSelectorStr
        )

        return lock and lock.locked

    def unlock(
        self, tupleDataSelector: TupleSelector, delegateUuid: str
    ) -> None:
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lockState = self._lockStateByDataSelectorByDataTupleType[
            tupleDataType
        ].get(tupleSelectorStr, None)

        if lockState:
            assert lockState.locked, (
                "TupleDataLiveLockManager: We received an request to unlock"
                " but the data is not locked. " + tupleSelectorStr
            )
            lockState.unlock(delegateUuid)

        self._observer.notifyOfTupleUpdate(
            _DataLockStatusTupleSelector.makeLockTupleSelector(
                lockState.tupleDataSelector
            )
        )

    def unlockAndMarkDeleted(
        self, tupleDataSelector: TupleSelector, delegateUuid: str
    ) -> None:
        tupleSelectorStr = tupleDataSelector.toJsonStr()
        tupleDataType = tupleDataSelector.name

        lockStateByDataSelector = self._lockStateByDataSelectorByDataTupleType[
            tupleDataType
        ]
        lockState = lockStateByDataSelector.get(
            tupleSelectorStr,
            _LockState(
                tupleDataSelector=tupleDataSelector,
            ),
        )

        lockState.delete(delegateUuid)

        lockStateByDataSelector[tupleSelectorStr] = lockState

        self._observer.notifyOfTupleUpdate(
            _DataLockStatusTupleSelector.makeLockTupleSelector(
                lockState.tupleDataSelector,
            )
        )

    @deferToThreadWrapWithLogger(logger)
    def makeLockVortexMsg(
        self, filt: dict, lockTupleSelector: TupleSelector
    ) -> bytes:
        dataTupleSelector = _DataLockStatusTupleSelector.getDataTupleSelector(
            lockTupleSelector
        )
        dataTupleType = dataTupleSelector.name
        lockStateByDataSelector = self._lockStateByDataSelectorByDataTupleType[
            dataTupleType
        ]
        lockState = lockStateByDataSelector.get(dataTupleSelector.toJsonStr())

        if lockState is None:
            results = [_DataLockStatusTuple(locked=False)]

        else:
            results = [
                _DataLockStatusTuple(
                    deleted=lockState.deleted,
                    locked=lockState.locked,
                    lockedByUserUuid=lockState.lockedByUserUuid,
                    lockAutoExpireDate=lockState.autoExpireDate,
                    liveUpdateDataFromDelegateUuid=lockState.liveUpdateDataFromDelegateUuid,
                    liveUpdateDataTuple=lockState.liveUpdateDataTuple,
                )
            ]

        payloadEnvelope = PayloadEnvelope(filt=filt)
        payloadEnvelope.encodedPayload = Payload(
            filt=filt, tuples=results
        ).toEncodedPayload()
        return payloadEnvelope.toVortexMsg()

    @deferToThreadWrapWithLogger(logger)
    def makeDataVortexMsg(
        self, filt: dict, dataTupleSelector: TupleSelector
    ) -> bytes:
        dataTupleType = dataTupleSelector.name
        lockStateByDataSelector = self._lockStateByDataSelectorByDataTupleType[
            dataTupleType
        ]
        lockState = lockStateByDataSelector.get(dataTupleSelector.toJsonStr())

        results = lockState.liveUpdateDataTuple

        payloadEnvelope = PayloadEnvelope(filt=filt)
        payloadEnvelope.encodedPayload = Payload(
            filt=filt, tuples=results
        ).toEncodedPayload()
        return payloadEnvelope.toVortexMsg()

    @deferToThreadWrapWithLogger(logger)
    def processLockTupleAction(
        self,
        tupleAction: _LockDataTupleAction,
        tupleActionVortex: TupleActionVortex,
    ):
        if tupleAction.lock:
            self._lock(tupleAction, tupleActionVortex)
        else:
            self.unlock(tupleAction.tupleDataSelector, tupleAction.delegateUuid)

        return
