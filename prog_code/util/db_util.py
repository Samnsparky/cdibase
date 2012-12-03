"""Logic for interfacing with application's persistance mechanism.

@author: Sam Pottinger
@license: GNU GPL v2
"""

import csv
import os
import sqlite3

import yaml

from ..struct import models

import file_util


def get_db_connection():
    """Get an open connection to the application database.

    @note: May come from connection pool.
    @return: Thread-specific connection to application database.
    @rtype: sqlite3.Connection
    """
    return sqlite3.connect('./db/daxlab.db')

def save_mcdi_model(newMetadataModel):
    """Save a metadata for a MCDI format.

    @param newMetadataModel: Model containing format metadata.
    @type newMetadataModel: models.MCDIFormatMetadata
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO mcdi_formats VALUES (?, ?, ?)",
        (
            newMetadataModel.safe_name,
            newMetadataModel.human_name,
            newMetadataModel.filename
        )
    )
    connection.commit()
    connection.close()


def delete_mcdi_model(metadataModelName):
    """Delete an existing saved MCDI format.

    @param metadataModelName: The name of the MCDI format to delete.
    @type metadataModelName: str
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM mcdi_formats WHERE safe_name=?",
        (metadataModelName,)
    )
    connection.commit()
    connection.close()


def load_mcdi_model_listing():
    """Load metadata for all MCDI formats.

    @return: Iterable over metadata for all MCDI formats..
    @rtype: Iterable over models.MCDIFormatMetadata
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT human_name,safe_name,filename FROM mcdi_formats"
    )
    ret_val = map(lambda x: models.MCDIFormatMetadata(x[0], x[1], x[2]), cursor)
    connection.close()
    return ret_val


def load_mcdi_model(name):
    """Load a complete MCDI format.

    @param name: The name of the MCDI format to load.
    @type name: str
    @return: MCDI format details and metadata.  None if MCDI format
        by the given name could not be found.
    @rtype: models.MCDIFormat
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        '''SELECT human_name,safe_name,filename FROM mcdi_formats
        WHERE safe_name=?''',
        (name,)
    )
    metadata = cursor.fetchone()
    connection.close()

    if metadata == None:
        return None

    filename = metadata[2]
    filename = os.path.join(file_util.UPLOAD_FOLDER, filename)
    with open(filename) as f:
        content = f.read()
    spec = yaml.load(content)

    return models.MCDIFormat(metadata[0], metadata[1], metadata[2], spec)


def save_presentation_model(newMetadataModel):
    """Save a presentation format.

    @param newMetadataModel: Model containing format metadata.
    @type newMetadataModel: models.PresentationFormatMetadata
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO presentation_formats VALUES (?, ?, ?)",
        (
            newMetadataModel.safe_name,
            newMetadataModel.human_name,
            newMetadataModel.filename
        )
    )
    connection.commit()
    connection.close()


def delete_presentation_model(metadataModel):
    """Delete an existing saved presentation format.

    @param metadataModelName: The name of the presentation format to delete.
    @type metadataModelName: str
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM presentation_formats WHERE safe_name=?",
        (metadataModel.safe_name,)
    )
    connection.commit()
    connection.close()


def load_presentation_model_listing():
    """Load metadata for all presentation formats.

    @return: Iterable over metadata for all MCDI formats..
    @rtype: Iterable over models.PresentationFormatMetadata
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT human_name,safe_name,filename FROM presentation_formats"
    )
    ret_val = map(lambda x: models.PresentationFormatMetadata(x[0], x[1], x[2]),
        cursor)
    connection.close()
    return ret_val


def load_presentation_model(name):
    """Load a complete MCDI format.

    @param name: The name of the MCDI format to load.
    @type name: str
    @return: MCDI format details and metadata. None if presentation format
        by the given name could not be found.
    @rtype: models.PresentationFormat
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        '''SELECT human_name,safe_name,filename FROM presentation_formats
        WHERE safe_name=?''',
        (name,)
    )
    metadata = cursor.fetchone()
    connection.close()

    if metadata == None:
        return None

    filename = metadata[2]
    filename = os.path.join(file_util.UPLOAD_FOLDER, filename)
    with open(filename) as f:
        content = f.read()
    spec = yaml.load(content)

    return models.PresentationFormat(metadata[0], metadata[1], metadata[2],
        spec)


def save_percentile_model(newMetadataModel):
    """Save a table of values necessary for calcuating child MCDI percentiles.

    @param name: The name of the precentile table model to load.
    @type name: str
    @return: MCDI format details and metadata.
    @rtype: models.PercentileTableMetadata
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO percentile_tables VALUES (?, ?, ?)",
        (
            newMetadataModel.safe_name,
            newMetadataModel.human_name,
            newMetadataModel.filename
        )
    )
    connection.commit()
    connection.close()


def delete_percentile_model(metadataModel):
    """Delete an existing saved percentile data table.

    @param metadataModelName: The name of the precentile table to delete.
    @type metadataModelName: str
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM percentile_tables WHERE safe_name=?",
        (metadataModel.safe_name,)
    )
    connection.commit()
    connection.close()


def load_percentile_model_listing():
    """Load metadata for all percentile tables.

    @return: Iterable over metadata for all percentile tables.
    @rtype: Iterable over models.PercentileTableMetadata
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT human_name,safe_name,filename FROM percentile_tables"
    )
    return map(lambda x: models.PercentileTableMetadata(x[0], x[1], x[2]),
        cursor)


def load_percentile_model(name):
    """Load a complete percentile table.

    @param name: The name of the percentile table to load.
    @type name: str
    @return: Percentile table contents and metadata. None if percentile table
        by the given name could not be found.
    @rtype: models.PercetileTable
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        '''SELECT human_name,safe_name,filename FROM percentile_tables
        WHERE safe_name=?''',
        (name,)
    )
    metadata = cursor.fetchone()
    connection.close()

    if metadata == None:
        return None

    filename = metadata[2]
    filename = os.path.join(file_util.UPLOAD_FOLDER, filename)
    with open(filename) as f:
        spec = list(csv.reader(f))

    return models.PercentileTable(metadata[0], metadata[1], metadata[2], spec)


def load_snapshot_contents(snapshot):
    """Load reports of individual statuses for words.

    Load status for individual / state of words as part of an MCDI snapshot.

    @param snapshot: The snapshot to get contents for.
    @type snapshot: model.SnapshotMetadata
    @return: Iterable over the details of the given MCDI snapshot.
    @rtype: Iterable over models.SnapshotContent
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM snapshot_content WHERE snapshot_id=?",
        (snapshot.database_id,)
    )
    ret_val = map(lambda x: models.SnapshotContent(*x), cursor.fetchall())
    connection.close()
    return ret_val


def load_user_model(email):
    """Load the user model for a user account with the given email address.

    @param email: The email of the user for which a user model should be
        retrieved.
    @type email: str
    @return: The user account information for the user with the given email
        address. None if corresponding user account cannot be found.
    @rtype: models.User
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )
    result = cursor.fetchone()
    connection.close()
    if not result:
        return None
    return models.User(*(result))


def save_user_model(user):
    """Save data about a user account.

    @param user: The user model to save to the database.
    @type user: models.User
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        '''UPDATE users SET password_hash=?,can_enter_data=?,can_access_data=?,
           can_change_formats=?,can_admin=? WHERE email=?''',
        (
            user.password_hash,
            user.can_enter_data,
            user.can_access_data,
            user.can_change_formats,
            user.can_admin,
            user.email
        )
    )
    connection.commit()
    connection.close()


def create_user_model(user):
    """Create a new user account.

    @param user: The new user account to persist to the database.
    @type user: models.User
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
        (
            user.email,
            user.password_hash,
            user.can_enter_data,
            user.can_access_data,
            user.can_change_formats,
            user.can_admin
        )
    )
    connection.commit()
    connection.close()


def delete_user_model(email):
    """Delete the user account with the given email address.

    @param email: The email address of the user account to delete.
    @type email: str
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM users WHERE email=?",
        (email,)
    )
    connection.commit()
    connection.close()


def get_all_user_models():
    """Get a listing of all user accounts for the web application.

    @return: Iterable over user account information.
    @rtype: Iterable over models.User
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    ret_val = map(lambda x: models.User(*x), cursor.fetchall())
    connection.close()
    return ret_val
