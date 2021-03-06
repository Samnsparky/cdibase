"""Logic for building CSV reports and zip archives of CSV files.

Copyright (C) 2014 A. Samuel Pottinger ("Sam Pottinger", gleap.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

@author: Sam Pottinger
@license: GNU GPL v3
"""

import csv
import io
import typing
import urllib.parse
import zipfile

import prog_code.util.constants as constants
import prog_code.util.db_util as db_util

import prog_code.struct.models as models

PRESENTATION_VALUE_NAME_MAP = {
    constants.NO_DATA: 'no_data',
    constants.UNKNOWN: 'unknown',
    constants.POSSIBLY_WRONGLY_REC: 'possibly_wrongly_recorded',
    constants.EMERGENCY_REC: 'emergency',
    constants.IMPLIED_FALSE: 'implied_false',
    constants.IMPLIED_TRUE: 'implied_true',
    constants.EXPLICIT_TRUE: 'explicit_true',
    constants.LEGACY_TRUE: 'explicit_true',
    constants.EXPLICIT_FALSE: 'explicit_false',
    constants.EXPLICIT_NONE: 'explicit_none',
    constants.EXPLICIT_NA: 'explicit_na',
    constants.EXPLICIT_OTHER: 'explicit_other',
    constants.NO_EXTRA_CATEGORIES: 'no_extra_categories',
    constants.EXTRA_CATEGORIES: 'extra_categories',
    constants.MALE: 'male',
    constants.FEMALE: 'female',
    constants.OTHER_GENDER: 'other_gender',
    constants.ELEVEN_PRESUMED_TRUE: 'explicit_true'
}

DEFAULT_CDI = 'fullenglishmcdi'


class NotFoundSnapshotContent:
    """A stand-in word snapshot content model.

    A word snapshot content model that represents that a word value is not
    available for a snapshot.
    """

    def __init__(self):
        """Create a new stand-in snapshot content model instance."""
        self.value = constants.NO_DATA


def interpret_word_value(value: int,
        presentation_format: typing.Optional[models.PresentationFormat]) -> typing.Union[str, int]:
    """Convert underlying special database value to a string descriptions.

    @param value: The value to get a string description for.
    @type value: int
    @param presentation_format: Presentation format information to use to
        convert the value to a string description.
    @type presentation_format: models.PresentationFormat
    @return: Description of the value or the original value if it is not
        indiciated as being special in the given presentation_format.
    @rtype: str or original value type
    """
    try:
        value = int(value)
    except ValueError:
        pass

    name = PRESENTATION_VALUE_NAME_MAP.get(value, value)

    presentation_format_realized: models.PresentationFormat = presentation_format # type: ignore

    if presentation_format == None or not name in presentation_format_realized.details:
        return value
    return presentation_format_realized.details[name]


def summarize_snapshots(snapshot_metas: typing.Iterable[models.SnapshotMetadata]) -> typing.Dict[
        str, typing.Any]:
    """Summarize snapshots as primitives.

    @param snapshot_metas: The snapshots to serialize.
    @return: The snapshots serialized into primitives.
    """
    cdi_spoken_set = {}
    ret_serialization: typing.Dict[str, typing.Any] = {}

    for meta in snapshot_metas:

        # Get the values that count as "spoken"
        cdi_name = meta.cdi_type
        cdi_date = meta.session_date
        if not cdi_name in cdi_spoken_set:
            cdi_info = db_util.load_cdi_model(cdi_name)
            assert cdi_info != None
            words_spoken_set = cdi_info.details['count_as_spoken'] # type: ignore
            cdi_spoken_set[cdi_name] = words_spoken_set
        else:
            words_spoken_set = cdi_spoken_set[cdi_name]

        # Parse the words
        contents = db_util.load_snapshot_contents(meta)
        for word_info in contents:
            word = word_info.word
            value = word_info.value

            # Replace existing if this snapshot is earlier
            if value in words_spoken_set:
                to_enter = not word in ret_serialization
                to_enter = to_enter or ret_serialization[word] == None
                to_enter = to_enter or ret_serialization[word] > cdi_date
                if to_enter:
                    ret_serialization[word] = cdi_date

            # Report not known if not already reported
            elif not word in ret_serialization:
                ret_serialization[word] = None

    return ret_serialization


def serialize_snapshot(snapshot: models.SnapshotMetadata,
        presentation_format: models.PresentationFormat = None,
        word_listing: typing.List[str] = None,
        report_dict: bool = False,
        include_words: bool = True) -> typing.Union[dict, typing.List]:
    """Turn a snapshot uft8 encoded list of strings.

    @param snapshot: The snapshot to serialize.
    @type snapshot: models.SnapshotMetadata
    @param presentation_format: The presentation format to use to render the
        string serialization.
    @type presentation_format: models.PresentationFormat
    @param word_listing: Vocabulary for the snapshot.
    @param report_dict: Flag indicating if the result should be a dictionary of primitives or list
        of values in sorted order.
    @param include_words: Flag indicating if the individual word values should be included.
    @return: Serialized version of the snapshot.
    @rtype: List of str
    """
    if not word_listing:
        word_listing = []

    if include_words:
        snapshot_contents = db_util.load_snapshot_contents(snapshot)
        snapshot_contents_dict = {}

        for entry in snapshot_contents:
            snapshot_contents_dict[entry.word.lower().replace('*', '')] = entry

        not_found_entry = NotFoundSnapshotContent()
        snapshot_contents_sorted = map(
            lambda x: snapshot_contents_dict.get(x.lower().replace('*', ''), not_found_entry),
            word_listing
        )

        word_values = list(map(
            lambda x: interpret_word_value(x.value, presentation_format),
            snapshot_contents_sorted
        ))

    if report_dict:
        gender = interpret_word_value(snapshot.gender, presentation_format)
        extra_categories = interpret_word_value(snapshot.extra_categories,
            presentation_format)
        return_dict = {
            'database_id': snapshot.database_id,
            'child_id': snapshot.child_id,
            'study_id': snapshot.study_id,
            'study': snapshot.study,
            'gender': gender,
            'age': snapshot.age,
            'birthday': snapshot.birthday,
            'session_date': snapshot.session_date,
            'session_num': snapshot.session_num,
            'total_num_sessions': snapshot.total_num_sessions,
            'words_spoken': snapshot.words_spoken,
            'items_excluded': snapshot.items_excluded,
            'percentile': snapshot.percentile,
            'extra_categories': extra_categories,
            'revision': snapshot.revision,
            'languages': ','.join(snapshot.languages),
            'num_languages': snapshot.num_languages,
            'cdi_type': snapshot.cdi_type,
            'hard_of_hearing': snapshot.hard_of_hearing,
            'deleted': snapshot.deleted
        }

        if include_words:
            return_dict['words'] = word_values # type: ignore

        return return_dict

    else:
        return_list = [
            snapshot.database_id,
            snapshot.child_id,
            snapshot.study_id,
            snapshot.study,
            interpret_word_value(snapshot.gender, presentation_format),
            snapshot.age,
            snapshot.birthday,
            snapshot.session_date,
            snapshot.session_num,
            snapshot.total_num_sessions,
            snapshot.words_spoken,
            snapshot.items_excluded,
            snapshot.percentile,
            interpret_word_value(snapshot.extra_categories, presentation_format),
            snapshot.revision,
            ','.join(snapshot.languages),
            snapshot.num_languages,
            snapshot.cdi_type,
            snapshot.hard_of_hearing,
            snapshot.deleted
        ]

        if include_words:
            return_list.extend(word_values)

        return return_list


def generate_study_report_rows(snapshots_from_study: typing.List[models.SnapshotMetadata],
        presentation_format: models.PresentationFormat) -> typing.List[typing.Tuple[str, typing.Any]]:
    """Serialize a set of snapshots to a collection of lists of strings.

    @param snapshots_by_study: The snapshots to serialize.
    @type snapshots_by_study: Iterable of models.SnapshotMetadata
    @param presentation_format: The presentation format to use to render the
        string serialization.
    @type: presentation_format: models.PresentationFormat
    @return: List of serialized versions of snapshots with first list with
        header information.
    @rtype: List of list of str.
    """
    word_listing_set: typing.Set[str] = set()
    for snapshot in snapshots_from_study:
        snapshot_contents = db_util.load_snapshot_contents(snapshot)
        candidate_word_listing = set(map(
            lambda x: x.word,
            snapshot_contents
        ))
        word_listing_set = word_listing_set.union(candidate_word_listing)

    word_listing = list(word_listing_set)
    word_listing.sort()

    serialized_snapshots = map(
        lambda x: serialize_snapshot(x, presentation_format, word_listing),
        snapshots_from_study
    )

    header_col = [
        'database id',
        'child id',
        'study id',
        'study',
        'gender',
        'age',
        'birthday',
        'session date',
        'session num',
        'total num sessions',
        'words spoken',
        'items excluded',
        'percentile',
        'extra categories',
        'revision',
        'languages',
        'num languages',
        'cdi type',
        'hard of hearing',
        'deleted'
    ]
    header_col.extend(word_listing)

    cols = [header_col]
    cols.extend(serialized_snapshots) # type: ignore

    return list(zip(*cols)) # type: ignore


def sort_by_study_order(rows: typing.List[typing.Any], cdi_format: models.CDIFormat) -> typing.List:
    """Sort report output rows such that they are in the same order as the CDI.

    Sort the reourt output rows such that the header rows come first followed
    by the word value rows in the same order as they appear in the original
    CDI.

    @param rows: The rows to sort including both the 20 header rows and the
        word value rows.
    @type rows: iterable over iterable over primitive
    @param cdi_format: Information about the presentation format whose
        CDI format should be sorted against.
    @type cdi_format: models.CDIFormat
    @return: Rows sorted acording to the presentation format.
    @rtype: iterable over iterable over primitive
    """
    categories = cdi_format.details['categories']
    word_index = {}
    i = 0
    for category in categories:
        for word in category['words']:
            word_index[word.lower().replace('*', '')] = i
            i+=1

    rows_header = rows[:20]
    def process(x):
        word_maybe_bytes = x[0]

        if isinstance(word_maybe_bytes, bytes):
            word = word_maybe_bytes.decode('utf-8')
        else:
            word = word_maybe_bytes

        word_lower = word.lower()
        word_lower
        word_clean = word_lower.replace('*', '')

        value = word_index.get(word_clean, -1)
        return (value, x)

    rows_content_indexed = list(map(
        process,
        rows[20:]
    ))
    rows_content_sorted = sorted(rows_content_indexed, key=lambda x: x[0])
    rows_content_sorted = list(map(lambda x: x[1], rows_content_sorted))
    return rows_header + rows_content_sorted


def generate_study_report_csv(snapshots_from_study: typing.List[models.SnapshotMetadata],
        presentation_format: models.PresentationFormat) -> io.StringIO:
    """Generate a CSV file for a set of snapshots with the same CDI format.

    @param snapshots_from_study: The snapshots to create a CSV report for.
    @type snapshots_from_study: Iterable over models.SnapshotMetadata
    @param presentation_format: The presentation format to use to render the
        string serialization.
    @type: presentation_format: models.PresentationFormat
    @return: Contents of the CSV file.
    @rtype: StringIO.StringIO
    """
    faux_file = io.StringIO()
    csv_writer = csv.writer(faux_file)
    cdi_type_name = snapshots_from_study[0].cdi_type
    safe_cdi_name = cdi_type_name.replace(' ', '')
    safe_cdi_name = urllib.parse.quote_plus(safe_cdi_name).lower()

    cdi_format = db_util.load_cdi_model(safe_cdi_name)
    if cdi_format == None:
        cdi_format = db_util.load_cdi_model(DEFAULT_CDI)

    assert cdi_format != None
    cdi_format_realized: models.CDIFormat = cdi_format #type: ignore

    rows = generate_study_report_rows(snapshots_from_study, presentation_format)
    rows = sort_by_study_order(rows, cdi_format_realized)

    def prep_string(target):
        if isinstance(target, bytes):
            return target.decode('utf-8')
        else:
            return target

    csv_writer.writerows(
        [[prep_string(val) for val in row] for row in rows]
    )
    return faux_file


def generate_consolidated_study_report(snapshots_iter: typing.Iterable[models.SnapshotMetadata],
        presentation_format: models.PresentationFormat) -> io.StringIO:
    """Generate a unified CSV file for a set of snapshots

    @param snapshots_iter: The snapshots to create a CSV report for.
    @type snapshots_iter: Iterable over models.SnapshotMetadata
    @param snapshots_iter: The presentation format to use to render the
        string serialization.
    @type: presentation_format: models.PresentationFormat
    @return: Contents of the zip archive file.
    @rtype: io.StringIO
    """
    snapshots = list(snapshots_iter)
    snapshots.sort(key=lambda x: '%s_%s' % (x.session_num, x.study_id))

    return generate_study_report_csv(
        snapshots,
        presentation_format
    )


def generate_study_report(snapshots, presentation_format):
    """Generate a zip archive for a set of snapshots

    Create a zip archive of CSV reports for a set of snapshots where each study
    gets an individual CSV file in the archive.

    @param snapshots_from_study: The snapshots to create a CSV report for.
    @type snapshots_from_study: Iterable over models.SnapshotMetadata
    @param presentation_format: The presentation format to use to render the
        string serialization.
    @type: presentation_format: models.PresentationFormat
    @return: Contents of the zip archive file.
    @rtype: io.StringIO
    """
    snapshots.sort(key=lambda x: '%s_%s' % (x.session_num, x.study_id))

    snapshots_by_study = {}
    for snapshot in snapshots:
        study = snapshot.study
        if not study in snapshots_by_study:
            snapshots_by_study[study] = []
        snapshots_by_study[study].append(snapshot)

    faux_files = {}
    for study_name in sorted(snapshots_by_study.keys()):
        report = generate_study_report_csv(
            snapshots_by_study[study_name],
            presentation_format
        )
        faux_files['%s.csv' % study_name] = report

    faux_zip_file = io.BytesIO()
    zip_file = zipfile.ZipFile(faux_zip_file, mode='w')
    for (filename, faux_file) in faux_files.items():
        zip_file.writestr(filename, faux_file.getvalue())

    return faux_zip_file
