"""Data models for common structures used in the application.

@author: Sam Pottinger
@license: GNU GPL v2
"""

class MCDIFormatMetadata:
    """Information about an MCDI format without the format itself."""

    def __init__(self, human_name, safe_name, filename):
        """Create a new metadata record.

        @param human_name: The name of this format intended for human eyes.
        @type human_name: str
        @param safe_name: The name of this format safe for use in URLs and
            lookup / unique identification.
        @type safe_name: str
        @param filename: The name of the file that contains the actual MCDI
            format specification.
        @type filename: str
        """
        self.human_name = human_name
        self.safe_name = safe_name
        self.filename = filename


class MCDIFormat(MCDIFormatMetadata):
    """A complete MCDI format specification with metadata."""

    def __init__(self, human_name, safe_name, filename, details):
        """Create a new specification record.

        @param human_name: The name of this format intended for human eyes.
        @type human_name: str
        @param safe_name: The name of this format safe for use in URLs and
            lookup / unique identification.
        @type safe_name: str
        @param filename: The name of the file that contains the actual MCDI
            format specification.
        @type filename: str
        @param details: Dictionary like object with specification contents.
        @type: dict or dict-like object
        """
        MCDIFormatMetadata.__init__(self, human_name, safe_name, filename)
        self.details = details


class ValueMapping:
    """Set of mappings from one value to another for.

    Set of value mappings for use in presentation / formatting transformations.
    """

    def __init__(self):
        """Create an empty mapping."""
        self.mapping = {}

    def add_mapping(self, orig_val, new_val):
        """Add a new mapping from orig_val to new_val in this set of mappings.

        @param orig_val: The starting value that should be transformed.
        @param new_val: The value that orig_val should be turned into.
        """
        self.mapping[orig_val] = new_val


class PresentationFormatMetadata:
    """Information about a CSV presentation format without the format itself."""
    
    def __init__(self, human_name, safe_name, filename):
        """Create a new metadata record.

        @param human_name: The name of this format intended for human eyes.
        @type human_name: str
        @param safe_name: The name of this format safe for use in URLs and
            lookup / unique identification.
        @type safe_name: str
        @param filename: The name of the file that contains the actual MCDI
            format specification.
        @type filename: str
        """
        self.human_name = human_name
        self.safe_name = safe_name
        self.filename = filename


class PresentationFormat(PresentationFormatMetadata):
    """A complete CSV presentation format specification with metadata."""
    
    def __init__(self, human_name, safe_name, filename, details):
        """Create a new specification record.

        @param human_name: The name of this format intended for human eyes.
        @type human_name: str
        @param safe_name: The name of this format safe for use in URLs and
            lookup / unique identification.
        @type safe_name: str
        @param filename: The name of the file that contains the actual MCDI
            format specification.
        @type filename: str
        @param details: Dictionary like object with specification contents.
        @type: dict or dict-like object
        """
        PresentationFormatMetadata.__init__(self, human_name, safe_name,
            filename)
        self.details = details


class PercentileTableMetadata:
    """Information about a precentile table without the table itself.

    Information about a table of values needed to calculate a child's MCDI
    percentile without the table itself.
    """

    def __init__(self, human_name, safe_name, filename):
        """Create a new metadata record.

        @param human_name: The name of this table intended for human eyes.
        @type human_name: str
        @param safe_name: The name of this table safe for use in URLs and
            lookup / unique identification.
        @type safe_name: str
        @param filename: The name of the file that contains the actual MCDI
            table specification.
        @type filename: str
        """
        self.human_name = human_name
        self.safe_name = safe_name
        self.filename = filename


class PercentileTable(PercentileTableMetadata):
    """Percentile table with metadata information.

    Table of values needed to calculate a child's MCDI percentile along with
    metadata about that table.
    """

    def __init__(self, human_name, safe_name, filename, details):
        """Create a new specification record.

        @param human_name: The name of this table intended for human eyes.
        @type human_name: str
        @param safe_name: The name of this table safe for use in URLs and
            lookup / unique identification.
        @type safe_name: str
        @param filename: The name of the file that contains the actual MCDI
            table specification.
        @type filename: str
        @param details: List of lists with table contents.
        @type: list of lists
        """
        PercentileTableMetadata.__init__(self, human_name, safe_name, filename)
        self.details = details


class SnapshotMetadata:
    """Information about a snapshot of a child's vocabulary (filled out MCDI)

    Metadata about an inventory of a child's vocabulary according to macarthur
    child development inventory.
    """

    def __init__(self, database_id, child_id, study_id, study, gender, age,
        birthday, session_date, session_num, total_num_sessions, words_spoken,
        items_excluded, percentile, extra_categories, revision, languages,
        num_languages, mcdi_type, hard_of_hearing):
        """Create a new snapshot metadata record.

        @param database_id: The ID for this snapshot.
        @type database_id: int
        @param child_id: The global database-wide ID for the child.
        @type child_id: int
        @param study_id: The study specific ID for the child (not guaranteed to
            be unique outside of study).
        @type study_id: str
        @param study: The name of this study this snapshot is part of.
        @type study: str
        @param gender: Constant corresponding to the gender of this child.
        @type gender: int. Specifically, constants.MALE, constants.FEMALE, or
            constants.OTHER_GENDER
        @param age: The age in months of this participant at the time of the
            study.
        @type age: int
        @param birthday: The birthday of the research participant. Should be in
            format YYYY/MM/DD
        @type birthday: str
        @param session_date: The date this snapshot was taken (YYYY/MM/DD)
        @type session_date: str
        @param session_num: The number of sessions that came before this session
            for this child as part of this study + 1.
        @type session_num: int
        @param total_num_sessions: The total number of sessions this participant
            is expected to have as of this snapshot as part of this study.
        @type total_num_sessions: int
        @param words_spoken: The number of MCDI words recorded as "spoken"
            (exact definition depends on MCDI format) at the time of this
            snapshot.
        @type words_spoken: int
        @param items_excluded: The number of items execluded during the
            administration of the MCDI for this snapshot.
        @type items_excluded: int
        @param percentile: The MCDI percentile of this child as measured by this
            snapshot.
        @type percentile: float
        @param extra_categories: The number of extra MCDI categories
            included during administeration of MCDI for this snapshot.
        @type extra_categories: int
        @param revision: The number of versions of this snapshot before this
            one.
        @type revision: int
        @param languages: CSV field of languages included in this MCDI.
        @type languages: str
        @param num_languages: The number of languages included in this MCDI.
        @type num_languages: int
        @param mcdi_type: The safe name of the MCDI format used for this
            snapshot.
        @type mcdi_type: str
        @param hard_of_hearing: Indicates if this child was indicated as hard
            of hearing at the time of this snapshot. This should be a value from
            constants.
        @type hard_of_hearing: int
        """
        self.database_id = database_id
        self.child_id = child_id
        self.study_id = study_id
        self.study = study
        self.gender = gender
        self.age = age
        self.birthday = birthday
        self.session_date = session_date
        self.session_num = session_num
        self.total_num_sessions = total_num_sessions
        self.words_spoken = words_spoken
        self.items_excluded = items_excluded
        self.percentile = percentile
        self.extra_categories = extra_categories
        self.revision = revision
        self.languages = languages
        self.num_languages = num_languages
        self.mcdi_type = mcdi_type
        self.hard_of_hearing = hard_of_hearing

    def __eq__(self, other):
        """Test to see if this snapshot has the same attribute values as other.

        Test to see if this snapshot metadata record has the same attribute
        values as another provided snapshot metadata record.

        @param other: The snapshot metdata record to compare this instance to.
        @type other: models.SnapshotMetadata
        @return: True if the instances have the same attribute values and False
            otherwise.
        @rtype: bool
        """
        if other == None:
            return False
        same = self.database_id == other.database_id
        same = self.child_id == other.child_id and same
        same = self.study_id == other.study_id and same
        same = self.study == other.study and same
        same = self.gender == other.gender and same
        same = self.age == other.age and same
        same = self.birthday == other.birthday and same
        same = self.session_date == other.session_date and same
        same = self.session_num == other.session_num and same
        same = self.total_num_sessions == other.total_num_sessions and same
        same = self.words_spoken == other.words_spoken and same
        same = self.items_excluded == other.items_excluded and same
        same = self.percentile == other.percentile and same
        same = self.extra_categories == other.extra_categories and same
        same = self.revision == other.revision and same
        same = self.languages == other.languages and same
        same = self.num_languages == other.num_languages and same
        same = self.mcdi_type == other.mcdi_type and same
        same = self.hard_of_hearing == other.hard_of_hearing and same
        return same


class SnapshotContent:
    """Record of a single MCDI word as part of a snapshot."""

    def __init__(self, snapshot_id, word, value, revision):
        """Creates a new SnapshotContent instance.

        @param snapshot_id: The database ID of the snapshot this record is part
            of.
        @type snapshot_id: int
        @param word: The word whose status is encoded in this record.
        @type word: str
        @param value: The value representing if this word was spoken or not or
            some other status indicator.
        @type value: Constant from util.constants
        @param revision: The number of versions of this record that existed
            before this one.
        @type revision: int
        """
        self.snapshot_id = snapshot_id
        self.word = word
        self.value = value
        self.revision = revision


class Filter:
    """A user-defined filter to apply when querying for data.

    A record of what a user is looking for when querying the database such that
    records with this property should be returned (AND clause with condition).
    """

    def __init__(self, field, operator, operand):
        """Creates a new Filter record of the form field operator operand.

        @param field: The field (safe name) of MCDI snapshot to filter data on.
        @type field: str
        @param operator: The equality operator to use.
        @type operator: str. Should be a key in filter_util.OPERATOR_MAP
        @param operand: The value to compare against.
        """
        self.field = field
        self.operator = operator
        self.operand = operand
        try:
            self.operand_float = float(self.operand)
        except ValueError:
            self.operand_float = None
        except TypeError:
            self.operand_float = None


class User:
    """Record of a user account providing someone access to DaxlabBase."""

    def __init__(self, db_id, email, password_hash, can_enter_data,
        can_delete_data, can_import_data, can_edit_parents, can_access_data,
        can_change_formats, can_use_api_key, can_admin):
        """Create a new User record.

        @param db_id: The unique numerical ID assigned to this user account in
            the database.
        @type db_id: int
        @param email: The email address of the user this record represents.
        @type email: str
        @param password_hash: The salted password hash of this user's password.
        @type password_hash: str / binary
        @param can_enter_data: Indicates if this user can add new data to the
            database.
        @type can_enter_data: bool
        @param can_delete_data: Indicates if this user can delete data from the
            database.
        @type can_delete_data: bool
        @param can_import_data: Indicates if this user can import data via CSV.
        @type can_import_data: bool
        @param can_access_data: Indicates if this user can download data from
            the database.
        @type can_access_data: bool
        @param can_change_formats: Inidicates if this user can edit MCDI
            formats, percentile tables, and CSV presentation settings.
        @type can_change_formats: bool
        @param can_use_api_key: Indicates if this user can use an API key.
        @type can_use_api_key: bool
        @param can_admin: Indicates if this user can edit other users' accounts
            and permissions.
        @type can_admin: bool
        """
        self.db_id = db_id
        self.email = email
        self.password_hash = password_hash
        self.can_enter_data = can_enter_data
        self.can_delete_data = can_delete_data
        self.can_import_data = can_import_data
        self.can_edit_parents = can_edit_parents
        self.can_access_data = can_access_data
        self.can_change_formats = can_change_formats
        self.can_use_api_key = can_use_api_key
        self.can_admin = can_admin


class ParentForm:
    """Record of a parent MCDI form that can be filled out online."""

    def __init__(self, form_id, child_name, parent_email, mcdi_type,
        database_id, study_id, study, gender, birthday, items_excluded,
        extra_categories, languages, num_languages, hard_of_hearing):
        """Create a new parent form record.

        Create a new parent form record. Note that this constructor does not
        persist this new record to the database.

        @param form_id: The unique ID to assign to this parent MCDI form.
        @type form_id: str
        @param child_name: The name of the child for which the MCDI report will
            be recorded.
        @type child_name: str
        @param parent_email: The email address of the parent who should recieve
            a link to this form by email.
        @type parent_email: str
        @param mcdi_type: The name of the MCDI format to present to the parent.
        @type mcdi_type: str
        @param database_id: The global ID of the child for which an MCDI form
            should be recorded.
        @type database_id: int
        @param study_id: The MCDI report resulting from this parent form will be
            associated with a study. This argument is the ID of the child within
            that study.
        @type study_id: str
        @param study: The MCDI report resulting from this parent form will be
            associated with a study. This argument is the name of the study that
            should be associated.
        @type study: str
        @param gender: Constant corresponding to the gender of this child.
        @type gender: int. Specifically, constants.MALE, constants.FEMALE, or
            constants.OTHER_GENDER
        @param birthday: The birthday of the research participant. Should be in
            format YYYY/MM/DD
        @type birthday: str
        @param items_excluded: The number of items execluded during the
            administration of the MCDI for this snapshot.
        @type items_excluded: int
        @param extra_categories: The number of extra MCDI categories
            included during administeration of MCDI for this snapshot.
        @type extra_categories: int
        @param languages: CSV field of languages included in this MCDI.
        @type languages: str
        @param num_languages: The number of languages included in this MCDI.
        @type num_languages: int
        @param mcdi_type: The safe name of the MCDI format used for this
            snapshot.
        @type mcdi_type: str
        @param hard_of_hearing: Indicates if this child was indicated as hard
            of hearing at the time of this snapshot. This should be a value from
            constants.
        @type hard_of_hearing: int
        """
        self.form_id = form_id
        self.child_name = child_name
        self.parent_email = parent_email
        self.mcdi_type = mcdi_type
        self.database_id = database_id
        self.study_id = study_id
        self.study = study
        self.gender = gender
        self.birthday = birthday
        self.items_excluded = items_excluded
        self.extra_categories = extra_categories
        self.languages = languages
        self.num_languages = num_languages
        self.hard_of_hearing = hard_of_hearing

    def __eq__(self, other):
        """Test to see if this form has the same attribute values as other.

        Test to see if this parent form record has the same attribute values as
        another provided parent form record.

        @param other: The parent form record to compare this instance to.
        @type other: models.ParentForm
        @return: True if the instances have the same attribute values and False
            otherwise.
        @rtype: bool
        """
        same = self.form_id == other.form_id
        same = same and self.child_name == other.child_name
        same = same and self.parent_email == other.parent_email
        same = same and self.mcdi_type == other.mcdi_type
        same = same and self.database_id == other.database_id
        same = same and str(self.study_id) == str(other.study_id)
        same = same and self.study == other.study
        same = same and self.gender == other.gender
        same = same and self.birthday == other.birthday
        same = same and self.items_excluded == other.items_excluded
        same = same and self.extra_categories == other.extra_categories
        same = same and self.languages == other.languages
        same = same and self.num_languages == other.num_languages
        same = same and self.hard_of_hearing == other.hard_of_hearing
        return same


class APIKey:
    """Record of an API key allowing programmatic access for a specific user."""

    def __init__(self, user_id, key):
        """Create a new API key record.

        @param user_id: The unique numerical ID of the user that this key
            belongs to.
        @type user_id: int
        @param key: A key this user can provide to programmatically access this
            application.
        @type key: str
        """
        self.user_id = user_id
        self.key = key
