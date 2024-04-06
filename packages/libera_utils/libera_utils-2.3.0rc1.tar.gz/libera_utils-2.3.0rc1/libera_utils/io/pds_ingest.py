"""Module for L0 file ingest"""
# Standard
import argparse
from datetime import datetime, timezone
import logging
import os
# Installed
from cloudpathlib import AnyPath
from botocore.exceptions import ClientError
# Local
from libera_utils.io.pds import ConstructionRecord, PDSRecord
from libera_utils.io.manifest import Manifest
from libera_utils.io.smart_open import smart_copy_file
from libera_utils.logutil import configure_task_logging
from libera_utils.io.filenaming import L0Filename
from libera_utils.db.dynamodb_utils import get_dynamodb_table
from libera_utils.config import config

logger = logging.getLogger(__name__)


class IngestDuplicateError(Exception):
    """Custom Exception for ingesting a duplicate into the DB"""

    def __init__(self, message, filename=None):
        self.filename = filename
        super().__init__(message)


def ingest(parsed_args: argparse.Namespace):
    """Ingest and update records into database using manifest
    Parameters
    ----------
    parsed_args : argparse.Namespace
        Namespace of parsed CLI arguments
        Must contain:
            manifest_filepath : str
                Path to manifest file to ingest

    Returns
    -------
    output_manifest_path : str
        Path of output manifest
    """
    now = datetime.now(timezone.utc).strftime("%Y%m%dt%H%M%S")
    configure_task_logging(f'l0_ingest_{now}',
                           app_package_name='libera_utils',
                           console_log_level=logging.DEBUG if parsed_args.verbose else None)
    logger.debug(f"CLI args: {parsed_args}")

    dropbox_processing_path = AnyPath(parsed_args.manifest_filepath).parent
    logger.debug(f"Processing dropbox set to {dropbox_processing_path}")

    metadata_ddb_table_name = config.get('METADATA_DDB_TABLE_NAME')
    logger.debug(f"Metadata table name set to {metadata_ddb_table_name}")

    # read json information
    logger.debug("Reading Manifest file")
    m = Manifest.from_file(parsed_args.manifest_filepath)
    m.validate_checksums()

    logger.info("Starting L0 ingest...")

    ingested_files = []
    for file in m.files:
        try:
            # TODO: Consider more error handling
            filepath = AnyPath(file["filename"])
            l0_file_name = L0Filename(filepath)
            if not filepath.is_absolute():
                raise ValueError(f"File path {filepath} is not an absolute filepath")
            if l0_file_name.filename_parts.file_number == 0:
                cr_ingest(filepath, dynamo_table_name=metadata_ddb_table_name)
                ingested_files.append(filepath)
            else:
                pds_ingest(filepath, dynamo_table_name=metadata_ddb_table_name)
                ingested_files.append(filepath)
        except IngestDuplicateError as error:
            # TODO what should we do with these files? Move them to the l0 dropbox? Keep them in the receiver bucket?
            logger.debug(f"The file {error.filename} already exists in the the DB and will not be included")
        except Exception as unhandled:
            logger.exception(unhandled)
            raise

    logger.debug(f"Files ingested from manifest: {ingested_files}")

    # Create output manifest file containing a list of the product files that the processing created
    output_manifest = Manifest.output_manifest_from_input_manifest(input_manifest=parsed_args.manifest_filepath)

    logger.info("Moving files from receiver bucket to dropbox as output data products")
    # move files to output directory
    for filepath in ingested_files:
        destination_location = dropbox_processing_path / os.path.basename(filepath)
        smart_copy_file(filepath, destination_location,
                        delete=parsed_args.delete)

        output_manifest.add_files(destination_location)

    # write output manifest to L0 ingest dropbox
    logger.info(f"Writing resulting output manifest to {dropbox_processing_path}")

    output_manifest.write(dropbox_processing_path)

    logger.info("L0 ingest algorithm complete. Exiting.")
    return str(output_manifest.filename.path.absolute())


def cr_ingest(filename: str or AnyPath, dynamo_table_name: str = None):
    """Ingest cr records into Postgres database
    Parameters
    ----------
    filename : str or AnyPath
        Filename of the construction record to be ingested
    dynamo_table_name : str, Optional
        Name of the DynamoDB table to use. Required if use_dynamo is True
    """
    filename_only = AnyPath(filename).name
    logger.info(f"Ingesting construction record with filename: {filename_only}")

    dynamo_table = get_dynamodb_table(dynamo_table_name)

    # Parse CR into nested dictionaries to insert into dynamo
    cr = ConstructionRecord.from_file(filename)
    cr_ddb = cr.to_ddb_items()
    write_capacity_units = 0
    for item in cr_ddb:
        try:
            response = dynamo_table.put_item(Item=item, ConditionExpression='attribute_not_exists(PK)',
                                             ReturnConsumedCapacity='TOTAL')
            write_capacity_units += float(response['ConsumedCapacity']['CapacityUnits'])
        except ClientError as error:
            if error.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.info(
                    f"Duplicate PDS file {filename} (in the DB and has an ingest time). Skipping DB insert.")
                raise IngestDuplicateError(f"Duplicate PDS file: {filename}", filename) from error
            raise error

    logger.info(f"Total write capacity units consumed for CR: {write_capacity_units}")
    return


def pds_ingest(filename: str or AnyPath, dynamo_table_name: str = None):
    """Ingest pd records into database that do not have an associated cr
    Parameters
    ----------
    filename : str or Any Path
        Filename of the PDS file to be ingested
    dynamo_table_name : str, Optional
        Name of the DynamoDB table to use. Required if use_dynamo is True
    """
    logger.info(f"Ingesting PDS file {filename}")
    filename_only = AnyPath(filename).name

    dynamo_table = get_dynamodb_table(dynamo_table_name)
    # Parse PDS into nested dictionaries to insert into dynamo
    pds = PDSRecord.from_filename(filename_only)
    pds_ddb_item = pds.to_ddb_pds_file_item()
    try:
        response = dynamo_table.put_item(Item=pds_ddb_item, ConditionExpression='attribute_not_exists(PK)',
                                         ReturnConsumedCapacity='TOTAL')
        write_capacity_units = float(response['ConsumedCapacity']['CapacityUnits'])
        logger.info(f"Total write capacity units consumed: {write_capacity_units}")
    except ClientError as error:
        if error.response['Error']['Code'] == 'ConditionalCheckFailedException':
            logger.info(f"Duplicate PDS file {filename} (in the DB and has an ingest time). Skipping DB insert.")
            raise IngestDuplicateError(f"Duplicate PDS file: {filename}", filename) from error
        raise error

    logger.info(f"Total write capacity units consumed: {response['ConsumedCapacity']['CapacityUnits']}")
    return
