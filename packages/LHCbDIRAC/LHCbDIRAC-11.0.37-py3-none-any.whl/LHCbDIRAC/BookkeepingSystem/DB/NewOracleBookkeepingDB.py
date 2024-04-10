###############################################################################
# (c) Copyright 2023 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from DIRAC import gLogger
from DIRAC.Core.Utilities.ReturnValues import S_OK, DReturnType, returnValueOrRaise, convertToReturnValue


class NewOracleBookkeepingDB:
    def __init__(self, *, dbW, dbR):
        self.log = gLogger.getSubLogger("LegacyOracleBookkeepingDB")
        self.dbW_ = dbW
        self.dbR_ = dbR

    def getAvailableFileTypes(self) -> DReturnType[list[str]]:
        """Retrieve all available file types from the database."""
        return self.dbR_.executeStoredProcedure("BOOKKEEPINGORACLEDB.getAvailableFileTypes", [])

    @convertToReturnValue
    def getFileTypesForProdID(self, prodID: int) -> list[str]:
        query_parts = [
            "SELECT DISTINCT filetypes.name",
            "FROM files, jobs, filetypes",
            "WHERE files.jobid = jobs.jobid AND jobs.production = :prodid AND filetypes.filetypeid = files.filetypeid",
        ]
        result = returnValueOrRaise(self.dbR_.query(" ".join(query_parts), kwparams={"prodid": prodID}))
        return [ft for ft, in result]

    @convertToReturnValue
    def getAvailableSMOG2States(self) -> list[str]:
        """Retrieve all available SMOG2 states."""
        result = returnValueOrRaise(self.dbR_.query("SELECT state FROM smog2"))
        return [state for state, in result]

    @convertToReturnValue
    def getRunsForSMOG2(self, state: str) -> list[int]:
        """Retrieve all runs with specified SMOG2 state

        :param str state: required state
        """
        query = "SELECT runs.runnumber FROM smog2 LEFT JOIN runs ON runs.smog2_id = smog2.id WHERE smog2.state = :state"
        result = returnValueOrRaise(self.dbR_.query(query, kwparams={"state": state}))
        return [run for run, in result]

    def setSMOG2State(self, state: str, update: bool, runs: list[int]) -> DReturnType[None]:
        """Set SMOG2 state for runs.

        :param str state: state for given runs
        :param bool update: when True, updates existing state, when False throw an error in such case
        :param list[int] runs: runs list
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.setSMOG2", parameters=[state, update], output=False, array=runs
        )

    def setExtendedDQOK(self, run: int, update: bool, dqok: list[str]) -> DReturnType[None]:
        """Set ExtendedDQOK for specified run and systems. In case update is allowed,
        not specified systems are unset for the run.

        :param int run: run number for which systems are specified
        :param bool update: when True, updates existing set, when False throw an error in such case
        :param list[str] dqok: list of system names
        """
        return self.dbW_.executeStoredProcedure(
            "BOOKKEEPINGORACLEDB.setExtendedDQOK", parameters=[run, update, dqok], output=False
        )

    @convertToReturnValue
    def getRunsWithExtendedDQOK(self, dqok: list[str]) -> list[int]:
        """Retrieve all runs with specified systems in ExtendedDQOK
        NOTE: it is NOT checking quality is set to OK, so it should NOT be used
        for end user operations.

        :param list[str] dqok: systems
        """
        if not dqok:
            return []
        sql = ["SELECT ok.runnumber FROM extendeddqok ok"]
        params = {"sysname0": dqok[0]}
        for i, system in enumerate(dqok[1::]):
            sql.append(
                f"INNER JOIN extendeddqok ok{i} ON ok{i}.runnumber = ok.runnumber AND ok{i}.systemname = :sysname{i}"
            )
            params[f"sysname{i}"] = system
        sql.append("WHERE ok.systemname = :sysname0")
        result = returnValueOrRaise(self.dbR_.query(" ".join(sql), kwparams=params))
        return [run for run, in result]

    @convertToReturnValue
    def getRunExtendedDQOK(self, runnb: int) -> list[str]:
        """Return the list of systems in ExtendedDQOK for given run

        :param int runnb: run number
        """
        query = "SELECT systemname FROM extendeddqok WHERE runnumber = :run"
        result = returnValueOrRaise(self.dbR_.query(query, kwparams={"run": runnb}))
        return [sysname for sysname, in result]
