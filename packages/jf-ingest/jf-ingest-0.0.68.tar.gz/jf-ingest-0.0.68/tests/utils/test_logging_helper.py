import logging

from jf_ingest import logging_helper

logger = logging.getLogger(__name__)


def _count_log_records_by_message(records):
    record_message_counts = {r.message: 0 for r in records}
    for record in records:
        record_message_counts[record.message] += 1

    return record_message_counts


def test_log_entry_exit_log_level(caplog):
    informational_log_message = "This is a test log"

    @logging_helper.log_entry_exit()
    def _test_function_for_wrapper():
        logging.info(informational_log_message)

    ########################################################################
    # TEST WITH LEVEL SET AT INFO (NO DEBUG MESSAGES SHOULD SHOW)
    ########################################################################
    caplog.set_level(level=logging.INFO)
    _test_function_for_wrapper()

    record_message_counts = _count_log_records_by_message(caplog.records)

    # Assert that the starting and ending log got called exactly once
    assert f"{_test_function_for_wrapper.__name__}: Starting" not in record_message_counts.keys()
    assert f"{_test_function_for_wrapper.__name__}: Ending" not in record_message_counts.keys()
    # Assert that the informational message appeared twice
    assert record_message_counts[informational_log_message] == 1
    assert len(caplog.records) == 1

    ########################################################################
    # TEST WITH LEVEL SET AT DEBUG
    ########################################################################
    # Reset caplog
    caplog.clear()
    caplog.set_level(level=logging.DEBUG)
    _test_function_for_wrapper()

    record_message_counts = _count_log_records_by_message(caplog.records)

    # Assert that the starting and ending log got called exactly once
    assert record_message_counts[f"{_test_function_for_wrapper.__name__}: Starting"] == 1
    assert record_message_counts[f"{_test_function_for_wrapper.__name__}: Ending"] == 1
    # Assert that the informational message appeared twice
    assert record_message_counts[informational_log_message] == 1
    assert len(caplog.records) == 3


def test_log_for_loop_iters_info_level(caplog):
    total_iters = 10
    log_every = 1

    ########################################################################
    # TEST WITH LEVEL SET AT INFO (NO DEBUG MESSAGES SHOULD SHOW)
    ########################################################################
    caplog.set_level(level=logging.INFO)
    logged_information_messages = []

    for i in range(10):
        with logging_helper.log_loop_iters("test_log_loop_iters", i, log_every):
            info_message = f"Iter {i}"
            logger.info(info_message)
            logged_information_messages.append(info_message)

    record_message_counts = _count_log_records_by_message(caplog.records)

    assert len(record_message_counts.keys()) == total_iters

    ########################################################################
    # TEST WITH LEVEL SET AT DEBUG
    ########################################################################
    caplog.clear()
    caplog.set_level(level=logging.DEBUG)

    for i in range(10):
        with logging_helper.log_loop_iters("test_log_loop_iters", i, log_every):
            info_message = f"Iter {i}"
            logger.info(info_message)
            logged_information_messages.append(info_message)

    record_message_counts = _count_log_records_by_message(caplog.records)

    # For every iter, we should have an additional 2
    assert len(record_message_counts.keys()) == (total_iters + (total_iters * 2))

    ########################################################################
    # TEST WITH LEVEL SET AT DEBUG (log every iter set to 2)
    ########################################################################
    log_every = 2
    caplog.clear()
    caplog.set_level(level=logging.DEBUG)

    for i in range(10):
        with logging_helper.log_loop_iters("test_log_loop_iters", i, log_every):
            info_message = f"Iter {i}"
            logger.info(info_message)
            logged_information_messages.append(info_message)

    record_message_counts = _count_log_records_by_message(caplog.records)

    # For every 2 iters, we should have an additional 2 debug logs
    assert len(record_message_counts.keys()) == (total_iters + (total_iters))


def test_log_standard_error_smoke_test(caplog):
    caplog.set_level(logging.WARNING)
    msg_args = ["TEST MESSAGE"]
    error_code = 0000
    logging_helper.log_standard_error(
        level=logging.WARNING, error_code=error_code, msg_args=msg_args
    )
    assert len(caplog.records) == 1
    assert caplog.records[0].message == logging_helper.generate_standard_error_msg(
        error_code=error_code, msg_args=msg_args
    )
