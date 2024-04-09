from enum import Enum


class ServiceTicketEventTriggerTypeEnum(str, Enum):
    MANUAL_CANCEL = "manual_cancel"
    BOOKING_REMINDING = "booking_reminding"
    MANUAL_TRACING_START = "manual_tracking_start"
    MANUAL_TRACING_STOP = "manual_tracking_stop"
    MANUAL_CREATE_SMWS = "manual_create_smws"
    MANUAL_IMPORT_RESERVATION_SMWS = "manual_import_reservation_smws"
    IMPORT_RESERVATION_CONFLICT_AUTO_CANCEL = "import_reservation_conflict_auto_cancel"
    LPNR_IN = "lpnr_in"
    LPNR_OUT = "lpnr_out"

