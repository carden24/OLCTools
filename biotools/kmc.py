from biotools import accessoryfunctions
import os
import shutil


def kwargs_to_string(kwargs):
    """
    Given a set of kwargs, turns them into a string which can then be passed to a command.
    :param kwargs: kwargs from a function call.
    :return: outstr: A string, which is '' if no kwargs were given, and the kwargs in string format otherwise.
    """
    outstr = ''
    for arg in kwargs:
        outstr += ' -{}{}'.format(arg, kwargs[arg])
    return outstr


def kmc(forward_in, database_name, min_occurrences=1, reverse_in='NA', k=31, cleanup=True,
        returncmd=False, tmpdir='tmp', **kwargs):
    """
    Runs kmc to count kmers.
    :param forward_in: Forward input reads. Assumed to be fastq.
    :param database_name: Name for output kmc database.
    :param min_occurrences: Minimum number of times kmer must be seen to be included in database.
    :param reverse_in: Reverse input reads. Automatically found.
    :param k: Kmer size. Default 31.
    :param cleanup: If true, deletes tmpdir that kmc needs.
    :param tmpdir: Temporary directory to store intermediary kmc files. Default tmp.
    :param returncmd: If true, will return the command used to call KMC as well as out and err.
    :param kwargs: Other kmc arguments in parameter='argument' format.
    :return: Stdout and stderr from kmc.
    """
    # Create the tmpdir kmc needs if it isn't already present.
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)
    options = kwargs_to_string(kwargs)
    if os.path.isfile(forward_in.replace('_R1', '_R2')) and reverse_in == 'NA' and '_R1' in forward_in:
        reverse_in = forward_in.replace('_R1', '_R2')
        filelist = os.path.join(tmpdir, 'filelist.txt')
        with open(filelist, 'w') as f:
            f.write(forward_in + '\n')
            f.write(reverse_in + '\n')
        cmd = 'kmc -k{} -ci{} {} @{} {} {}'.format(k, min_occurrences, options, filelist, database_name, tmpdir)
    elif reverse_in == 'NA':
        cmd = 'kmc -k{} -ci{} {} {} {} {}'.format(k, min_occurrences, options, forward_in, database_name, tmpdir)
    else:
        filelist = os.path.join(tmpdir, 'filelist.txt')
        with open(filelist, 'w') as f:
            f.write(forward_in + '\n')
            f.write(reverse_in + '\n')
        cmd = 'kmc -k{} -ci{} {} @{} {} {}'.format(k, min_occurrences, options, filelist, database_name, tmpdir)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if cleanup:
        shutil.rmtree(tmpdir)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def intersect(database_1, database_2, results, returncmd=False):
    """
    Finds kmers that are present in 2 databases.
    :param database_1: First database generated by kmc.
    :param database_2: Second database generated by kmc.
    :param results: Result database, containing reads in both database 1 and 2.
    :param returncmd: If true, will return the command used to call KMC as well as out and err.
    :return: Stdout and stderr from kmc.
    """
    cmd = 'kmc_tools intersect {} {} {}'.format(database_1, database_2, results)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def union(database_1, database_2, results, returncmd=False):
    """
    Finds kmers that are present in either of the two databases provided (as well as reads found in both).
    :param database_1: First database generated by kmc.
    :param database_2: Second database generated by kmc.
    :param results: Result database, containing reads in either database 1 or 2 (or both).
    :param returncmd: If true, will return the command used to call KMC as well as out and err.
    :return: Stdout and stderr from kmc.
    """
    cmd = 'kmc_tools union {} {} {}'.format(database_1, database_2, results)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def subtract(database_1, database_2, results, exclude_below=1, returncmd=False):
    """
    Subtracts database 2 from database 1. Results can then be dumped to view what kmers are present only in database 1.
    :param database_1: First database generated by kmc.
    :param database_2: Second database generated by kmc.
    :param results: Result database, containing reads in both database 1 but not in 2..
    :param exclude_below: Don't subtract kmers from database 1 that have less than this many occurrences
    in database 2.
    :param returncmd: If true, will return the command used to call KMC as well as out and err.
    :return: Stdout and stderr from kmc.
    """
    cmd = 'kmc_tools kmers_subtract {} {} -ci{} {}'.format(database_1, database_2, str(exclude_below), results)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def dump(database, output, min_occurences=1, max_occurences=250, returncmd=False):
    """
    Dumps output from kmc database into tab-delimited format.
    :param database: Database generated by kmc.
    :param output: Name for output.
    :param min_occurences: Minimum number of times kmer must be in database to be dumped.
    :param max_occurences: Maximum number of times a kmer can be seen and still be dumped.
    :param returncmd: If true, will return the command used to call KMC as well as out and err.
    :return: Stdout and stderr from kmc.
    """
    cmd = 'kmc_tools dump -ci{} -cx{} {} {}'.format(min_occurences, max_occurences, database, output)
    out, err = accessoryfunctions.run_subprocess(cmd)
    if returncmd:
        return out, err, cmd
    else:
        return out, err


def percentage_in(query_database, reference_database, intdb='intersection',
                  int_dump='intersection_dumped', ref_dump='reference_dumped',
                  tmpdir='tmp', cleanup=True):
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)
    intersect_database = os.path.join(tmpdir, intdb)
    intersect(query_database, reference_database, intersect_database)
    intersect_dump = os.path.join(tmpdir, int_dump)
    reference_dump = os.path.join(tmpdir, ref_dump)
    dump(reference_database, reference_dump)
    dump(intersect_database, intersect_dump)
    try:
        percentage = float(accessoryfunctions.file_len(intersect_dump)/float(accessoryfunctions.file_len(reference_dump)))
    except ZeroDivisionError:
        percentage = -1.0
    if cleanup:
        shutil.rmtree(tmpdir)
    return percentage
