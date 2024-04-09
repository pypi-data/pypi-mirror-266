from python_sdk_remote.mini_logger import MiniLogger

from .Connector import get_connection

failed_logger = False
failed_location = False


class Writer:
    @staticmethod  # TODO: not used. Can we / shall we have one add_message...()  method?
    def add_message(message: str, severity_id: int) -> None:
        global failed_logger
        if failed_logger:
            return  # Don't try again if failed
        MiniLogger.info("add_message" + message + ' ' + str(severity_id),
                        object={"message": message, "log_level": severity_id})
        connection = None
        try:
            # creating connection
            connection = get_connection(schema_name="logger")
            cursor = connection.cursor()

            query = ("INSERT INTO logger.logger_table (message, severity_id) "
                     "VALUES (%s, %s)")
            cursor.execute(query, (message, severity_id))
        except Exception as exception:
            MiniLogger.exception("Exception Writer.py Writer.add_message caught", exception)
            failed_logger = True
        finally:
            if connection:
                connection.commit()

    # TODO We prefer to have one INSERT to the logger_table
    # INSERT to logger_table should be disabled by default and activated using combination of json and Environment variable enabling INSERTing to the logger_table
    # This function is called `if self.write_to_sql and self.debug_mode.is_logger_output(component_id=
    #                               self.component_id, logger_output=LoggerOutputEnum.MySQLDatabase, message_severity.value)`
    @staticmethod
    def add_message_and_payload(message: str = None, **kwargs) -> None:
        global failed_logger, failed_location
        if failed_logger:
            return  # Don't try again if failed
        connection = None
        try:
            connection = get_connection(schema_name="logger")
            params_to_insert = kwargs['object']

            try:
                if not failed_location:
                    cursor = connection.cursor()
                    location_query = (f"INSERT INTO location.location_table (coordinate) "
                                      f"VALUES (POINT({params_to_insert.get('latitude') or 0},"
                                      f"              {params_to_insert.get('longitude') or 0}));")
                    cursor.execute(location_query)
                    coordinate_id = cursor.lastrowid

                    params_to_insert.pop('latitude', None)
                    params_to_insert.pop('longitude', None)

                    params_to_insert['location_id'] = coordinate_id
            except Exception as exception:
                MiniLogger.exception("Exception logger Writer.py add_message_and_payload ", exception)
                failed_location = True

            listed_values = [str(k) for k in params_to_insert.values()]
            joined_keys = ','.join(list(params_to_insert.keys()))
            if 'message' not in params_to_insert:
                listed_values.append(message)
                joined_keys += (',' if params_to_insert else '') + 'message'

            placeholders = ','.join(['%s'] * len(listed_values))
            logger_query = f"INSERT INTO logger.logger_table ({joined_keys}) VALUES ({placeholders})"
            cursor = connection.cursor()
            cursor.execute(logger_query, listed_values)
        except Exception as exception:
            MiniLogger.exception("Exception logger Writer.py add_message_and_payload ", exception)
            if " denied " not in str(exception).lower():
                raise exception
            failed_logger = True
        finally:
            if connection:
                connection.commit()
