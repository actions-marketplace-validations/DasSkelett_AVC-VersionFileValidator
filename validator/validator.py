import json
import logging as log
from pathlib import Path
from typing import Set

import jsonschema
import requests

from .ksp_version import KspVersion
from .versionfile import VersionFile


# Returns (status, successful, failed, ignored)
def validate_cwd(exclude) -> (int, Set[Path], Set[Path], Set[Path]):
    all_exclusions = calculate_all_exclusions(exclude)

    # GH will set the cwd of the container to the so-called workspace, which is a clone of the triggering repo,
    # assuming the user remembered to add the 'actions/checkout' step before.
    found_files = {f for f in Path().rglob('*')
                   if f.is_file() and f.suffix.lower() == '.version'}

    version_files = found_files.difference(all_exclusions)
    successful_files = set()
    failed_files = set()
    ignored_files = found_files.intersection(all_exclusions)

    log.info(f'Ignoring {[str(f) for f in ignored_files]}')

    if not version_files:
        log.warning('No version files found.')
        return 0, successful_files, failed_files, ignored_files

    log.info(f'Found {[str(f) for f in version_files]}')
    schema = get_schema()
    if not schema:
        return 1, successful_files, failed_files, ignored_files
    build_map = get_build_map()

    for f in version_files:
        try:
            # The actual validation happens here.
            check_single_file(f, schema, KspVersion(list(build_map.get('builds').values())[-1]))
        except json.decoder.JSONDecodeError as e:
            log.error(f'Failed loading {str(f)} as JSON. Check for syntax errors around the mentioned line: {e}')
            failed_files.add(f)
            continue
        except jsonschema.ValidationError as e:
            log.error(f'Validation of {f} failed: {e}')
            failed_files.add(f)
            continue

        successful_files.add(f)

    log.debug('Done!')
    if failed_files:
        log.error(f'The following files failed validation: {[str(f) for f in failed_files]}')
        return 1, successful_files, failed_files, ignored_files
    else:
        return 0, successful_files, failed_files, ignored_files


def calculate_all_exclusions(exclude: str) -> Set[Path]:
    all_exclusions = set()
    if exclude and not exclude.isspace():
        try:
            globs = json.loads(exclude)
        except json.decoder.JSONDecodeError:
            # Not a valid JSON array, assume it is a single exclusion glob
            globs = [exclude]

        # If someone passes a string like this: '"./*.version"'
        if isinstance(globs, str):
            globs = [globs]

        for _glob in globs:
            all_exclusions = all_exclusions.union(Path().glob(_glob))
    return all_exclusions


def get_schema():
    log.debug('Fetching schema...')
    try:
        return requests.get(
            'https://github.com/linuxgurugamer/KSPAddonVersionChecker/raw/master/KSP-AVC.schema.json'
        ).json()
    except ValueError:
        log.error('Current schema not valid JSON, that\'s unfortunate...')
        return None


def get_build_map():
    log.debug('Fetching build map...')
    try:
        return requests.get('https://github.com/KSP-CKAN/CKAN-meta/raw/master/builds.json').json()
    except requests.exceptions.RequestException:
        log.debug('Failed downloading build map from the CKAN-meta repository.')
    except ValueError:
        log.debug('Current build map is not valid JSON, that\'s unfortunate...')
    return None


def check_single_file(f: Path, schema, latest_ksp):
    log.debug(f'Loading {f}')
    with f.open('r') as vf:
        version_file = VersionFile(vf.read())

    log.debug(f'Validating {f}')
    version_file.validate(schema, False)
    if not version_file.is_compatible_with_ksp(latest_ksp):
        log.warning(f"The file {f} doesn't indicate compatibility "
                    f"with the latest version of KSP ({str(latest_ksp)}). "
                    f"Did you forget to update it?")

    # Check remote version file
    if remote := version_file.get_remote():
        try:
            remote.validate(schema)
            try:
                if not remote.is_compatible_with_ksp(latest_ksp):
                    log.warning(f"The remote version file of {f} doesn't indicate compatibility "
                                f"with the latest version of KSP ({str(latest_ksp)}). "
                                f"Did you forget to update it? {version_file.url}")
            except:
                pass

        except requests.exceptions.RequestException as e:
            log.error(f'Failed downloading remote version file at {version_file.url}. '
                      'Note that the URL property, when used, '
                      'must point to the "Location of a remote version file for update checking":')
            raise e
        except json.decoder.JSONDecodeError as e:
            log.error(f'Failed loading remote version file at {version_file.url}. '
                      'Note that the URL property, when used, '
                      'must point to the "Location of a remote version file for update checking":')
            raise e
        except jsonschema.ValidationError as e:
            log.error(f'Validation failed for remote version file at {version_file.url}. '
                      'Note that the URL property, when used, '
                      'must point to the "Location of a remote version file for update checking":')
            raise e

    log.info(f'Validation of {str(f)} successful.')
