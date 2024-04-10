from pydmclab.core.struc import StrucTools
from pydmclab.hpc.vasp import VASPSetUp
from pydmclab.hpc.analyze import AnalyzeVASP
from pydmclab.utils.handy import read_yaml, write_yaml
from pydmclab.data.configs import (
    load_vasp_configs,
    load_slurm_configs,
    load_sub_configs,
    load_partition_configs,
)

from pymatgen.core.structure import Structure
from pymatgen.io.lobster import Lobsterin


import multiprocessing as multip
import os
from shutil import copyfile, rmtree
import subprocess
import warnings

from subprocess import call

from pymatgen.io.vasp.sets import get_structure_from_prev_run

HERE = os.path.dirname(os.path.abspath(__file__))


class SubmitTools(object):
    """
    This class is focused on figuring out how to prepare chains of calculations
        the idea being that the output from this class is some file that you can
            "submit" to a queueing system
        this class will automatically crawl through the VASP output files and figure out
            how to edit that submission file to finish the desired calculations

    """

    def __init__(
        self,
        launch_dir,
        final_xcs,
        magmom,
        user_configs={},
        refresh_configs=["vasp", "sub", "slurm"],
        vasp_configs_yaml=os.path.join(os.getcwd(), "_vasp_configs.yaml"),
        slurm_configs_yaml=os.path.join(os.getcwd(), "_slurm_configs.yaml"),
        sub_configs_yaml=os.path.join(os.getcwd(), "_sub_configs.yaml"),
    ):
        """
        Args:
            launch_dir (str)
                directory to launch calculations from (to submit the submission file)
                    assumes initial structure is POSCAR in launch_dir
                        pydmclab.hpc.launch.LaunchTools will put it there
                within this directory, various VASP calculation directories (calc_dirs) will be created
                        gga-loose, gga-relax, gga-static, etc
                            VASP will be run in each of these, but we need to run some sequentially, so we pack them together in one submission script

            final_xcs (list)
                list of exchange correlation methods we want the final energy for
                you should pass this to SubmitTools
                    pydmclab.hpc.launch.LaunchTools will put it there
                e.g., ['metagga'] if you only want metagga or ['ggau', 'metagga'] if you want both of these methods

            magmom (list)
                list of magnetic moments for each atom in structure (or None if not AFM)
                    you should pass this here or let pydmclab.hpc.launch.LaunchTools put it there
                None if not AFM
                if AFM, pull it from a dictionary of magmoms you made with MagTools

            user_configs (dict)
                any non-default parameters you want to pass
                these will override the defaults in the yaml files
                look at pydmc/data/data/*configs*.yaml for the defaults
                    note: _launch_configs.yaml will be modified using LaunchTools
                you should be passing stuff here!
                    VASPSetUp will expect xc_to_run, calc_to_run, standard, and mag
                        xc_to_run and calc_to_run will be passed based on final_xcs and sub_configs['packing']
                        standard and mag will get passed to it based on launch_dir
                you can also pass any settings in _vasp_configs.yaml, _slurm_configs.yaml, or _sub_configs.yaml here
                    _vasp_configs options:
                        how to manipulate the VASP inputs
                        see pydmclab.hpc.vasp or pydmclab.data.data._vasp_configs.yaml for options
                    _sub_configs options:
                        how to manipulate the executables in the submission script and packing of calculations
                        see pydmclab.hpc.submit or pydmclab.data.data._sub_configs.yaml for options
                    _slurm_configs options:
                        how to manipulate the slurm tags in the submission script
                        see pydmclab.data.data._slurm_configs.yaml for options

            vasp_configs_yaml (os.pathLike)
                path to yaml file containing baseline vasp configs
                    there's usually no reason to change this
                    this holds some default configs for VASP
                    can always be changed with user_configs

             slurm_configs_yaml (os.pathLike)
                path to yaml file containing baseline slurm configs
                    there's usually no reason to change this
                    this holds some default configs for slurm
                    can always be changed with user_configs

            sub_configs_yaml (os.pathLike)
                path to yaml file containing baseline submission file configs
                    there's usually no reason to change this
                    this holds some default configs for submission files
                    can always be changed with user_configs

            refresh_configs (bool)
                if True, will copy pydmclab baseline configs to your local directory
                    this is useful if you've made changes to the configs files in the directory you're working in and want to start over

        Returns:
            self.launch_dir (os.pathLike)
                directory to launch calculations from

            self.slurm_configs (dict)
                dictionary of slurm configs (in format similar to yaml)

            self.vasp_configs (dict)
                dictionary of vasp configs (in format similar to yaml)

            self.sub_configs (dict)
                dictionary of submission configs (in format similar to yaml)

            self.structure (Structure)
                pymatgen structure object from launch_dir/POSCAR

            self.partitions (dict)
                dictionary of info regarding partition configurations on MSI

            self.final_xcs (list)
                list of exchange correlation methods we want the final energy for
        """

        self.launch_dir = launch_dir

        # just a reminder of how a launch directory looks
        # NOTE: should be made with LaunchTools
        top_level, unique_ID, standard, mag = launch_dir.split("/")[-4:]

        # don't run gga twice
        if ("gga" in final_xcs) and ("metagga" in final_xcs):
            warnings.warn(
                "You have both gga and metagga in final_xcs. This is probably not what you want. I'm going to remove gga from final_xcs since you get it for free w/ metagga"
            )
            final_xcs.remove("gga")

        # copy baseline vasp configs to launch_dir if they don't exist
        if not os.path.exists(vasp_configs_yaml) or ("vasp" in refresh_configs):
            _vasp_configs = load_vasp_configs()
            write_yaml(_vasp_configs, vasp_configs_yaml)

        # copy baseline slurm configs to launch_dir if they don't exist
        if not os.path.exists(slurm_configs_yaml) or ("slurm" in refresh_configs):
            _slurm_configs = load_slurm_configs()
            write_yaml(_slurm_configs, slurm_configs_yaml)

        # copy baseline sub configs to launch_dir if they don't exist
        if not os.path.exists(sub_configs_yaml) or ("sub" in refresh_configs):
            _sub_configs = load_sub_configs()
            write_yaml(_sub_configs, sub_configs_yaml)

        # we're going to modify vasp, slurm, and sub configs using one user_configs dict, so let's keep track of what's been applied
        user_configs_used = []

        # update slurm_configs based on user_configs
        slurm_configs = read_yaml(slurm_configs_yaml)
        for option in slurm_configs:
            if option in user_configs:
                if option not in user_configs_used:
                    new_value = user_configs[option]
                    slurm_configs[option] = new_value
                    user_configs_used.append(option)

        # create copy of slurm_configs to prevent unwanted updates
        self.slurm_configs = slurm_configs.copy()

        # update sub_configs based on user_configs
        sub_configs = read_yaml(sub_configs_yaml)
        for option in sub_configs:
            if option in user_configs:
                if option not in user_configs_used:
                    new_value = user_configs[option]
                    sub_configs[option] = new_value
                    user_configs_used.append(option)

        # create copy of sub_configs to prevent unwanted updates
        self.sub_configs = sub_configs.copy()

        # update vasp_configs based on user_configs
        vasp_configs = read_yaml(vasp_configs_yaml)
        for option in vasp_configs:
            if option in user_configs:
                if option not in user_configs_used:
                    new_value = user_configs[option]
                    vasp_configs[option] = new_value
                    user_configs_used.append(option)

        # determine standard and mag from launch_dir
        vasp_configs["standard"] = standard
        vasp_configs["mag"] = mag

        # include magmom in vasp_configs
        vasp_configs["magmom"] = magmom

        # create copy of vasp_configs to prevent unwanted updates
        self.vasp_configs = vasp_configs.copy()

        # need a POSCAR to initialize setup
        # LaunchTools should take care of this
        fpos = os.path.join(launch_dir, "POSCAR")
        if not os.path.exists(fpos):
            raise FileNotFoundError(
                "Need a POSCAR to initialize setup; POSCAR not found in {}".format(
                    self.launch_dir
                )
            )
        else:
            self.structure = Structure.from_file(fpos)

        # load partition configurations to help with slurm setup
        partitions = load_partition_configs()
        self.partitions = partitions

        # these are the xcs we want energies for --> each one of these should have a submission script
        # i.e., they are the end of individual chains
        self.final_xcs = final_xcs

    @property
    def queue_manager(self):
        """
        Returns queue manager (eg #SBATCH)
        """
        return self.sub_configs["manager"]

    @property
    def slurm_options(self):
        """
        Returns dictionary of slurm options
            - nodes, ntasks, walltime, etc

        To be written at the top of submission files
        """
        slurm_configs = self.slurm_configs.copy()
        options = {
            option: slurm_configs[option]
            for option in slurm_configs
            if slurm_configs[option]
        }
        partitions = self.partitions.copy()
        if options["partition"] in partitions:
            partition_specs = partitions[options["partition"]]

            # make special amendments for GPU partitions
            if partition_specs["proc"] == "gpu":
                options["nodes"] = 1
                options["ntasks"] = 1
                options["gres"] = "gpu:%s:%s" % (
                    options["partition"].split("-")[0],
                    str(options["nodes"]),
                )

            # reduce walltime if needed
            max_time = partition_specs["max_wall"] / 60
            if options["time"] > max_time:
                options["time"] = max_time

            # reduce nodes if needed
            max_nodes = int(partition_specs["max_nodes"])
            if options["nodes"] > max_nodes:
                options["nodes"] = max_nodes

            # reduce ntasks if needed
            max_cores_per_node = int(partition_specs["cores_per_node"])
            if options["ntasks"] / options["nodes"] > max_cores_per_node:
                options["ntasks"] = max_cores_per_node * options["nodes"]

            # warn user if they are using non-sharing nodes but not requesting all cores
            if not partition_specs["sharing"]:
                if options["ntasks"] / options["nodes"] < max_cores_per_node:
                    print(
                        "WARNING: this node cant be shared but youre not using all of it ?"
                    )
        return options

    @property
    def bin_dir(self):
        """
        Returns bin directory where things (eg LOBSTER) are located
        """
        sub_configs = self.sub_configs.copy()
        machine = sub_configs["machine"]
        if machine == "msi":
            return "/home/cbartel/shared/bin"
        elif machine == "bridges2":
            return "/ocean/projects/mat230011p/shared/bin"
        elif machine == "expanse":
            return "/home/%s/bin/" % os.getlogin()
        else:
            raise NotImplementedError('dont have bin path for machine "%s"' % machine)

    @property
    def vasp_dir(self):
        """
        Returns directory containing vasp executable
        """
        machine = self.sub_configs["machine"]
        version = self.sub_configs["vasp_version"]
        if machine == "msi":
            preamble = "%s/vasp" % self.bin_dir
            if version == 5:
                return "%s/vasp.5.4.4.pl2" % preamble
            elif version == 6:
                return "%s/vasp.6.4.1" % preamble
        elif machine == "bridges2":
            if version == 6:
                return "/opt/packages/VASP/VASP6/6.3+VTST"
            else:
                raise NotImplementedError("VASP < 6 not on Bridges?")
        else:
            raise NotImplementedError('dont have VASP path for machine "%s"' % machine)

    @property
    def vasp_command(self):
        """
        Returns command used to execute vasp
            e.g., 'srun -n 24 PATH_TO_VASP/vasp_std > vasp.o' (if mpi_command == 'srun')
            e.g., 'mpirun -np 24 PATH_TO_VASP/vasp_std > vasp.o' (if mpi_command == 'mpirun')
        """
        sub_configs = self.sub_configs.copy()
        vasp_configs = self.vasp_configs.copy()
        vasp_exec = os.path.join(self.vasp_dir, sub_configs["vasp"])
        slurm_options = self.slurm_options.copy()

        if sub_configs["mpi_command"] == "srun":
            return "\n%s --ntasks=%s --mpi=pmi2 %s > %s\n" % (
                sub_configs["mpi_command"],
                str(slurm_options["ntasks"]),
                vasp_exec,
                vasp_configs["fvaspout"],
            )
        elif sub_configs["mpi_command"] == "mpirun":
            return "\n%s -np=%s %s > %s\n" % (
                sub_configs["mpi_command"],
                str(slurm_options["ntasks"]),
                vasp_exec,
                vasp_configs["fvaspout"],
            )

    @property
    def lobster_command(self):
        """
        Returns command used to execute lobster
        """
        lobster_path = os.path.join(
            self.bin_dir, "lobster", "lobster-4.1.0", "lobster-4.1.0"
        )
        return "\n%s\n" % lobster_path

    @property
    def bader_command(self):
        """
        Returns command used to execute bader
        """
        chgsum = "%s/bader/chgsum.pl AECCAR0 AECCAR2" % self.bin_dir
        bader = "%s/bader/bader CHGCAR -ref CHGCAR_sum" % self.bin_dir
        return "\n%s\n%s\n" % (chgsum, bader)

    def is_job_in_queue(self, job_name):
        """
        Args:
            job_name (str)
                name of job to check if in queue
                generated automatically by SubmitTools.prepare_directories using launch_dir
                    ".".join(launch_dir.split("/")[-4:] + [final_xc])

                beware that having two calculations with the same name will cause problems

        Returns:
            True if this job-name is already in the queue, else False

        will prevent you from messing with directories that have running/pending jobs
        """
        # create a file w/ jobs in queue with my username and this job_name
        scripts_dir = os.getcwd()
        fqueue = os.path.join(scripts_dir, "_".join(["q", job_name]) + ".o")
        with open(fqueue, "w") as f:
            subprocess.call(
                ["squeue", "-u", "%s" % os.getlogin(), "--name=%s" % job_name], stdout=f
            )

        # get the job names I have in the queue
        names_in_q = []
        with open(fqueue) as f:
            for line in f:
                if "PARTITION" not in line:
                    names_in_q.append([v for v in line.split(" ") if len(v) > 0][2])

        # delete the file I wrote w/ the queue output
        os.remove(fqueue)

        # if this job is in the queue, return True
        if len(names_in_q) > 0:
            print(" !!! job already in queue, not messing with it")
            return True

        print(" not in queue, onward --> ")
        return False

    @property
    def prepare_directories(self):
        """
        This gets called by SubmitTools.write_sub, so you should rarely call this on its own

        A lot going on here. The objective is to prepare a set of directories for all calculations of interest to a given submission script in a given launch_dir
            note: 1 submission script --> 1 chain (pack) of VASP calculations
            note: 1 launch_dir --> can have > 1 submission script (if working towards >1 "final_xc" like ['metagga', 'ggau'])

        1) For each xc-calc pair, create a directory (calc_dir)
            */launch_dir/xc-calc
                xc-calc could be gga-loose, metagga-relax, etc.

        2) Check if that calc_dir has a converged VASP job
            note: also checks "parents" (ie a static is labeled unconverged if its relax is unconverged)
                parents determined by sub_configs['packing']

            if calc and parents are converged:
                checks sub_configs['fresh_restart']
                    if fresh_restart = False --> label calc_dir as status='done' and move on
                    if fresh_restart = True --> label calc_dir as status='new' and start this calc over

        3) Put */launch_dir/POSCAR into */launch_dir/xc-calc/POSCAR if there's not a POSCAR there already

        4) Check if */calc_dir/CONTCAR exists and has data in it,
            if it does, copy */calc_dir/CONTCAR to */calc_dir/POSCAR and label status='continue' (ie continuing job)
            if it doesn't, label status='new' (ie new job)

        5) Initialize VASPSetUp for calc_dir
            modifies VASPSetUp(calc_dir).get_vasp_input with self.vasp_configs

        6) If status in ['continue', 'new'],
            check for errors using VASPSetUp(calc_dir).error_msgs
                may remove WAVECAR/CHGCAR
                will likely make edits to INCAR
        """

        # make copies of relevant configs dicts
        vasp_configs = self.vasp_configs.copy()
        sub_configs = self.sub_configs.copy()

        fresh_restart = sub_configs["fresh_restart"]
        launch_dir = self.launch_dir

        # determine the terminal ends of each chain of VASP calcs to be submitted
        final_xcs = self.final_xcs

        # determine how VASP jobs get chained together
        packing = sub_configs["packing"]

        if sub_configs["skip_loose"]:
            new_packing = {}
            for xc in packing:
                new_packing[xc] = []
                for calc in packing[xc]:
                    if "loose" not in calc:
                        new_packing[xc].append(calc)
            packing = new_packing.copy()

        print("\n\n~~~~~ starting to work on %s ~~~~~\n\n" % launch_dir)

        fpos_src = os.path.join(launch_dir, "POSCAR")

        # loop through all calculations within each chain and collect statuses
        # statuses = {final_xc : {xc_calc : status}}
        statuses = {}

        # looping through each chain
        for final_xc in final_xcs:
            # create a job name from the launch_dir
            job_name = ".".join(launch_dir.split("/")[-4:] + [final_xc])

            # make sure job isnt in the queue
            print("\nchecking if %s is in q" % job_name)
            if self.is_job_in_queue(job_name):
                # if it is, on to the next job
                continue

            statuses[final_xc] = {}

            # looping through each VASP calc in that chain
            for xc_calc in packing[final_xc]:
                # initialize configs that are particular to this particular VASP calc in this chain
                calc_configs = {}

                # (0) update vasp configs with the current xc and calc
                xc_to_run, calc_to_run = xc_calc.split("-")
                calc_configs["xc_to_run"] = xc_to_run
                calc_configs["calc_to_run"] = calc_to_run

                # (1) make calc_dir (or remove and remake if fresh_restart)
                calc_dir = os.path.join(launch_dir, xc_calc)
                if os.path.exists(calc_dir) and fresh_restart:
                    rmtree(calc_dir)
                if not os.path.exists(calc_dir):
                    os.mkdir(calc_dir)

                # (2) check convergence of current calc
                E_per_at = AnalyzeVASP(calc_dir).E_per_at
                convergence = True if E_per_at else False

                # (3) if converged, make sure parents have converged
                large_E_diff_between_relax_and_static = False
                if convergence:
                    # static calcs are currently the only ones that have parents that must be converged
                    if calc_to_run == "static":
                        static_energy = E_per_at

                        # that parent is a relax
                        parent_calc = "relax"
                        parent_xc_calc = "%s-%s" % (xc_to_run, parent_calc)

                        # make sure we're calculating relax and static (and not just)
                        if parent_xc_calc in packing[final_xc]:
                            parent_calc_dir = os.path.join(launch_dir, parent_xc_calc)
                            parent_energy = AnalyzeVASP(parent_calc_dir).E_per_at
                            parent_convergence = True if parent_energy else False
                            if not parent_energy:
                                print(
                                    "     %s (parent) not converged, need to continue this calc"
                                    % parent_xc_calc
                                )
                            else:
                                # if there is a large difference b/t the relax and static energy, something fishy happened, so let's start the static calc over
                                if abs(parent_energy - static_energy) > 0.05:
                                    print(
                                        "     %s (parent) and %s (child) energies differ by more than 0.2 eV/atom"
                                        % (parent_xc_calc, xc_calc)
                                    )
                                    large_E_diff_between_relax_and_static = True
                        else:
                            parent_convergence = True
                    else:
                        parent_convergence = True

                    if calc_to_run == "static":
                        # to consider a static done, check:
                        # convergence
                        # parent convergence
                        # if we want fresh restart
                        # if the relax and static energies are too different
                        # for statics, also check if we want to force postprocess
                        # this means re-compute the static so we can re-run lobster, bader, etc
                        if (
                            convergence
                            and parent_convergence
                            and not fresh_restart
                            and not large_E_diff_between_relax_and_static
                            # note: muting force_postprocess here b/c we want the calc to still be "done", right?
                            # and not sub_configs["force_postprocess"]
                        ):
                            print("     %s is already converged; skipping" % xc_calc)
                            status = "done"
                            statuses[final_xc][xc_calc] = status
                            continue
                    else:
                        if convergence and parent_convergence and not fresh_restart:
                            print("     %s is already converged; skipping" % xc_calc)
                            status = "done"
                            statuses[final_xc][xc_calc] = status
                            continue

                # for jobs that are not DONE:

                # (4) check for POSCAR
                # flag to check whether POSCAR is newly copied (don't want to perturb already-perturbed structures)
                fpos_dst = os.path.join(calc_dir, "POSCAR")
                if os.path.exists(fpos_dst):
                    # if there is a POSCAR, make sure its not empty
                    with open(fpos_dst, "r") as f_tmp:
                        contents = f_tmp.readlines()
                    # if its empty, copy the initial structure to calc_dir
                    if len(contents) == 0:
                        copyfile(fpos_src, fpos_dst)

                # if theres no POSCAR, copy the initial structure to calc_dir
                if not os.path.exists(fpos_dst):
                    copyfile(fpos_src, fpos_dst)

                # (5) check for CONTCAR. if one exists, if its not empty, and if not fresh_restart, mark this job as one to "continue"
                # (ie later, we'll copy CONTCAR to POSCAR); otherwise, mark as NEWRUN
                fcont_dst = os.path.join(calc_dir, "CONTCAR")
                if os.path.exists(fcont_dst):
                    with open(fcont_dst, "r") as f_tmp:
                        contents = f_tmp.readlines()
                    if (
                        (len(contents) > 0)
                        and not fresh_restart
                        and not large_E_diff_between_relax_and_static
                    ):
                        status = "continue"
                    else:
                        status = "new"
                else:
                    status = "new"

                statuses[final_xc][xc_calc] = status

                # set our user_configs based on our vasp_configs + our calc_configs
                # note: vasp_configs should hold the baseline vasp_configs + our user_configs
                # note: calc_configs should just hold xc_to_run and calc_to_run as of now
                user_vasp_configs_before_error_handling = {
                    **vasp_configs,
                    **calc_configs,
                }

                # (6) initialize VASPSetUp with current VASP configs for this calculation
                vsu = VASPSetUp(
                    calc_dir=calc_dir,
                    user_configs=user_vasp_configs_before_error_handling,
                )

                user_vasp_configs = user_vasp_configs_before_error_handling.copy()

                # (7) check for errors in continuing jobs
                incar_changes = {}
                if status in ["continue", "new"]:
                    calc_is_clean = vsu.is_clean
                    if not calc_is_clean:
                        # change INCAR based on errors and include in calc_configs
                        incar_changes = vsu.incar_changes_from_errors

                # if there are INCAR updates, add them to calc_configs
                if incar_changes:
                    incar_key = "%s_incar" % calc_to_run
                    for setting in incar_changes:
                        user_vasp_configs[incar_key][setting] = incar_changes[setting]

                # print("\n\n\n\n\n\n")
                # print(calc_dir)
                # print("THESE ARE MY USER_VASP_CONFIGS")
                # print(user_vasp_configs)
                # print("\n\n\n\n\n\n")
                # print(calc_dir)

                # update our vasp_configs with any modifications to the INCAR that we made to fix errors
                # user_vasp_configs = {**vasp_configs, **calc_configs}
                print("--------- may be some warnings (POTCAR ones OK) ----------")

                # (8) prepare calc_dir to launch
                vsu = VASPSetUp(calc_dir=calc_dir, user_configs=user_vasp_configs)

                vsu.prepare_calc

                print("-------------- warnings should be done ---------------")
                print("\n~~~~~ prepared %s ~~~~~\n" % calc_dir)
        return statuses

    @property
    def write_sub(self):
        """
        A lot going on here. The objective is to write a submission script for each pack of VASP calculations
            each submission script will launch a chain of jobs
            this gets a bit tricky because a submission script is executed in bash
                it's essentially like moving to a compute node and typing each line of the submission script into the compute node's command line
                this means we can't really use python while the submission script is being executed

        1) check if job's in queue. if it is, just return (ie don't work on that job)

        2) write our slurm options at the top of sub file (#SBATCH ...)

        3) loop through all the calculations we want to do from this launch dir
            label them as "done", "continue", or "new"

        4) for "continue"
            copy CONTCAR to POSCAR to save progress

        5) for "new" and "continue"
            figure out what parent calculations to get data from
                e.g., gga-static for metagga-relax
            make sure that parent calculation finished without errors before passing data to next calc
                and before running next calc
                if a parent calc didnt finish, but we've moved onto the next job, kill the job, so we can (automatically) debug the parent calc

        6) write VASP commands

        7) if lobster_static and calc is static, write LOBSTER and BADER commands
        """

        # make copies of our starting configs
        vasp_configs = self.vasp_configs.copy()
        sub_configs = self.sub_configs.copy()

        # determine which files will be passed from parent calcs to children
        files_to_inherit = sub_configs["files_to_inherit"]

        launch_dir = self.launch_dir

        vasp_command = self.vasp_command
        slurm_options = self.slurm_options.copy()
        queue_manager = self.queue_manager

        # determine how jobs will be chained together
        packing = sub_configs["packing"]

        if sub_configs["skip_loose"]:
            new_packing = {}
            for xc in packing:
                new_packing[xc] = []
                for calc in packing[xc]:
                    if "loose" not in calc:
                        new_packing[xc].append(calc)
            packing = new_packing.copy()

        # get our statuses from when we prepared VASP input files for each directory
        # statuses = {final_xc : {xc_calc : status}}
        # e.g., statuses['metagga']['gga-relax'] = 'done'
        statuses = self.prepare_directories
        for final_xc, v in statuses.items():
            # initialize a submission script for this chain
            # this is what we'll launch with sbatch sub_...sh
            fsub = os.path.join(launch_dir, "sub_%s.sh" % final_xc)

            # initialize a status log file for this chain
            # this is where we'll print status updates (helpful for debugging)
            fstatus = os.path.join(launch_dir, "status_%s.o" % final_xc)

            # create a job name based on the launch_dir
            # e.g., formula.ID.standard.mag.final_xc
            job_name = ".".join(launch_dir.split("/")[-4:] + [final_xc])

            # make sure job is not in queue already
            print("\nchecking if %s is in q" % job_name)
            if self.is_job_in_queue(job_name):
                continue
            slurm_options["job-name"] = job_name

            # if job isnt in queue already, start writing our submission script
            with open(fsub, "w", encoding="utf-8") as f:
                # slurm requires this header
                f.write("#!/bin/bash -l\n")

                # write the SLURM stuff (partition, nodes, time, etc) at the top
                for key in slurm_options:
                    slurm_option = slurm_options[key]
                    if slurm_option:
                        f.write(
                            "%s --%s=%s\n" % (queue_manager, key, str(slurm_option))
                        )
                f.write("\n\n")

                # this is for running MPI jobs that may require large memory
                f.write("ulimit -s unlimited\n")

                # load certain modules if needed for MPI command
                if sub_configs["mpi_command"] == "mpirun":
                    if sub_configs["machine"] == "msi":
                        if sub_configs["vasp_version"] == 5:
                            f.write("module load impi/2018/release_multithread\n")
                        elif sub_configs["vasp_version"] == 6:
                            unload = [
                                "mkl",
                                "intel/2018.release",
                                "intel/2018/release",
                                "impi/2018/release_singlethread",
                                "mkl/2018.release",
                                "impi/intel",
                            ]
                            load = ["mkl/2021/release", "intel/cluster/2021"]
                            for module in unload:
                                f.write("module unload %s\n" % module)
                            for module in load:
                                f.write("module load %s\n" % module)
                    elif sub_configs["machine"] == "bridges2":
                        f.write("module load intelmpi\nexport OMP_NUM_THREADS=1\n")

                # now write what is needed for the chain of VASP calcs + postprocessing
                print("\n:::: writing sub now - %s ::::" % fsub)

                # use this counter to figure if there are parents for a given calc and who those parents are
                xc_calc_counter = -1
                for xc_calc in packing[final_xc]:
                    # loop through the calculations that should be chained together for a given final_xc
                    xc_calc_counter += 1

                    # grab the status
                    status = statuses[final_xc][xc_calc]

                    # find our calc_dir (where VASP is executed for this xc_calc)
                    xc_to_run, calc_to_run = xc_calc.split("-")
                    calc_dir = os.path.join(launch_dir, xc_calc)
                    f.write(
                        "\necho working on %s _%s_ >> %s\n" % (xc_calc, status, fstatus)
                    )
                    if status == "done":
                        # write postprocessing commands for static calculations if needed
                        if calc_to_run == "static":
                            if vasp_configs["lobster_static"]:
                                if sub_configs[
                                    "force_postprocess"
                                ] or not os.path.exists(
                                    os.path.join(calc_dir, "lobsterout")
                                ):
                                    f.write("cd %s\n" % calc_dir)
                                    f.write(self.lobster_command)
                                if sub_configs[
                                    "force_postprocess"
                                ] or not os.path.exists(
                                    os.path.join(calc_dir, "ACF.dat")
                                ):
                                    f.write("cd %s\n" % calc_dir)
                                    f.write(self.bader_command)

                                # see if our bandstructure can be set up
                                if vasp_configs["generate_bandstructure"]:
                                    bs_dir = setup_bandstructure(
                                        converged_static_dir=calc_dir,
                                        rerun=sub_configs["force_postprocess"],
                                        symprec=vasp_configs["bs_symprec"],
                                        kpoints_line_density=vasp_configs[
                                            "bs_line_density"
                                        ],
                                    )
                                else:
                                    bs_dir = None

                                if bs_dir:
                                    # if it can, go to that directory, run VASP, run LOBSTER
                                    f.write(
                                        "echo working on %s-bs >> %s\n"
                                        % (xc_calc, fstatus)
                                    )
                                    f.write("cd %s\n" % bs_dir)
                                    f.write("%s\n" % vasp_command)
                                    f.write(self.lobster_command)

                            # see if you PARCHG can be set up
                            if vasp_configs["generate_parchg"]:
                                parchg_dir = setup_parchg(
                                    converged_static_dir=calc_dir,
                                    rerun=sub_configs["force_postprocess"],
                                    eint=vasp_configs["eint_for_parchg"],
                                )
                            else:
                                parchg_dir = None

                            if parchg_dir:
                                f.write(
                                    "echo working on %s-parchg >> %s\n"
                                    % (xc_calc, fstatus)
                                )
                                f.write("cd %s\n" % parchg_dir)
                                f.write("%s\n" % vasp_command)

                            if vasp_configs["generate_finite_displacements"]:
                                phonon_dir = generate_finite_displacements(
                                    converged_static_dir=calc_dir,
                                    supercell_grid=vasp_configs[
                                        "supercell_grid_for_finite_displacements"
                                    ],
                                )
                                print('phonon_dir = "%s"' % phonon_dir)
                            else:
                                phonon_dir = None

                            if phonon_dir:

                                disp_statuses = setup_finite_displacement_calcs(
                                    phonon_dir
                                )
                                print(">>> here are disp statuses: ", disp_statuses)
                                for disp in disp_statuses:
                                    disp_dir = disp_statuses[disp]["calc_dir"]
                                    convergence = disp_statuses[disp]["convergence"]
                                    if convergence:
                                        continue

                                    f.write(
                                        "echo working on %s-phonon-%s >> %s\n"
                                        % (xc_calc, disp, fstatus)
                                    )
                                    f.write("cd %s\n" % disp_dir)
                                    f.write("%s\n" % vasp_command)

                            if vasp_configs["generate_dfpt"]:
                                phonon_dir = setup_dfpt(
                                    converged_static_dir=calc_dir,
                                    supercell_grid=vasp_configs[
                                        "supercell_grid_for_dfpt"
                                    ],
                                )
                            else:
                                phonon_dir = None

                            if phonon_dir:
                                f.write(
                                    "echo working on %s-dfpt >> %s\n"
                                    % (xc_calc, fstatus)
                                )
                                f.write("cd %s\n" % phonon_dir)
                                f.write("%s\n" % vasp_command)
                                f.write("phonopy --fc vasprun.xml\n")

                            if vasp_configs["generate_magtest"]:
                                magtest_dir = setup_static_magtest(
                                    converged_static_dir=calc_dir
                                )
                            else:
                                magtest_dir = None

                            if magtest_dir:
                                f.write(
                                    "echo working on %s-static_magtest >> %s\n"
                                    % (xc_calc, fstatus)
                                )
                                f.write("cd %s\n" % magtest_dir)
                                f.write("%s\n" % vasp_command)

                        f.write("echo %s is done >> %s\n" % (xc_calc, fstatus))
                    else:
                        if status == "continue":
                            # copy the CONTCAR to the POSCAR
                            f.write(
                                "cp %s %s\n"
                                % (
                                    os.path.join(calc_dir, "CONTCAR"),
                                    os.path.join(calc_dir, "POSCAR"),
                                )
                            )

                        # figure out if we need to pass data from a parent calculation
                        pass_info = False if xc_calc_counter == 0 else True
                        if pass_info:
                            # who's the parent
                            parent_xc_calc = packing[final_xc][xc_calc_counter - 1]

                            # this will be the "source" directory where we get files from
                            src_dir = os.path.join(launch_dir, parent_xc_calc)

                            # before passing data, make sure parent has finished without crashing (using bash..)
                            f.write(
                                "isInFile=$(cat %s | grep -c %s)\n"
                                % (os.path.join(src_dir, "OUTCAR"), "Elaps")
                            )
                            f.write("if [ $isInFile -eq 0 ]; then\n")
                            f.write(
                                '   echo "%s is not done yet so this job is being killed" >> %s\n'
                                % (parent_xc_calc, fstatus)
                            )

                            # cancel job if parent crashed (no Elaps in OUTCAR)
                            f.write("   scancel $SLURM_JOB_ID\n")
                            f.write("fi\n")

                            # pass files that need to be inherited
                            for file_to_inherit in files_to_inherit:
                                # don't pass WAVECARs from loose since KPOINTS will change
                                if ("loose" in parent_xc_calc) and (
                                    file_to_inherit == "WAVECAR"
                                ):
                                    continue
                                fsrc = os.path.join(src_dir, file_to_inherit)

                                # copy CONTCAR of finished job to POSCAR of next job
                                if file_to_inherit == "CONTCAR":
                                    fdst = os.path.join(calc_dir, "POSCAR")
                                else:
                                    fdst = os.path.join(calc_dir, file_to_inherit)
                                if file_to_inherit == "CONTCAR":
                                    # make sure CONTCAR is not empty
                                    if os.path.exists(fsrc):
                                        with open(fsrc, "r", encoding="utf-8") as f_tmp:
                                            contents = f_tmp.readlines()
                                        if len(contents) < 0:
                                            continue
                                f.write("cp %s %s\n" % (fsrc, fdst))

                        # navigate to calculation directory and run vasp
                        f.write("cd %s\n" % calc_dir)
                        f.write("%s\n" % vasp_command)

                        # include postprocessing stuff as requested
                        if vasp_configs["lobster_static"]:
                            if calc_to_run == "static":
                                if (
                                    not os.path.exists(
                                        os.path.join(calc_dir, "lobsterout")
                                    )
                                    or sub_configs["force_postprocess"]
                                ):
                                    f.write(self.lobster_command)
                                if (
                                    not os.path.exists(
                                        os.path.join(calc_dir, "ACF.dat")
                                    )
                                    or sub_configs["force_postprocess"]
                                ):
                                    f.write(self.bader_command)
                        f.write(
                            "\necho launched %s-%s >> %s\n"
                            % (xc_to_run, calc_to_run, fstatus)
                        )
                f.write("\n\nscancel $SLURM_JOB_ID\n")
        return True

    @property
    def launch_sub(self):
        """
        launch the submission script written in write_sub
            if job is not in queue already
            if there's something to launch
                (ie if all calcs are done, dont launch)
        """
        final_xcs = self.final_xcs

        print("     now launching sub")
        scripts_dir = os.getcwd()
        launch_dir = self.launch_dir

        # determine what keywords to look for to see if job needs to be launched
        flags_that_need_to_be_executed = self.sub_configs["execute_flags"]

        for final_xc in final_xcs:
            # identify the submission script for this chain
            fsub = os.path.join(launch_dir, "sub_%s.sh" % final_xc)
            with open(fsub) as f:
                for line in f:
                    if "job-name" in line:
                        job_name = line[:-1].split("=")[-1]

            # see if jobs in queue
            if self.is_job_in_queue(job_name):
                continue

            needs_to_launch = False
            # see if there's anything to launch
            with open(fsub) as f:
                contents = f.read()
                for flag in flags_that_need_to_be_executed:
                    if flag in contents:
                        needs_to_launch = True

            if not needs_to_launch:
                print(" !!! nothing to launch here, not launching\n\n")
                return

            # if we made it this far, launch it
            os.chdir(launch_dir)
            subprocess.call(["sbatch", "sub_%s.sh" % final_xc])
            os.chdir(scripts_dir)


def setup_bandstructure(
    converged_static_dir, rerun=False, symprec=0.1, kpoints_line_density=20
):
    """

    function to create input files (INCAR, KPOINTS, POTCAR, POSCAR, lobsterin) for band structure calculations
        after static calculations

    ideally, this would be implemented as the end of a "packing" but slightly complicated because we need teh static calculation to be converged (or do we?)

    Args:
        converged_static_dir (str)
            path to converged static calculation

        rerun (bool)
            if True, rerun bandstructure calculation even if it's already converged

        symprec (float)
            symmetry precision for finding primitive cell and generating KPOINTS

        kpoints_line_density (int)
            how many kpoints between each high symmetry point

    Returns:
        directory to band structure calculation (str) or None if not ready to run this

    """
    # make sure static is converged
    av = AnalyzeVASP(converged_static_dir)
    if not av.is_converged:
        print("static calculation not converged; not setting up bandstructure yet")
        return None

    # get the paths to relevant input files from the static calculation
    files_from_static = ["POSCAR", "KPOINTS", "POTCAR", "INCAR"]
    fposcar_src, fkpoints_src, fpotcar_src, fincar_src = [
        os.path.join(converged_static_dir, f) for f in files_from_static
    ]

    # make a directory for the bandstructure calculation
    bs_dir = converged_static_dir.replace("-static", "-bs")
    if not os.path.exists(bs_dir):
        os.mkdir(bs_dir)

    # get the paths to relevant input files for the bandstructure calculation
    fposcar_dst, fkpoints_dst, fpotcar_dst, fincar_dst = [
        os.path.join(bs_dir, f) for f in files_from_static
    ]

    # make sure bandstructure calc didn't already run
    av = AnalyzeVASP(bs_dir)
    if av.is_converged and not rerun:
        print("bandstructure already converged")
        return None

    # initialize a Lobsterin object
    lobsterin = Lobsterin

    # create a primitive cell and write to bs POSCAR (needed so we don't have a bunch of overlapping bands)
    lobsterin.write_POSCAR_with_standard_primitive(
        POSCAR_input=fposcar_src, POSCAR_output=fposcar_dst, symprec=symprec
    )

    # create a line-mode KPOINTS file and write to bs KPOINTS
    try:
        lobsterin.write_KPOINTS(
            POSCAR_input=fposcar_dst,
            KPOINTS_output=fkpoints_dst,
            line_mode=True,
            symprec=symprec,
            kpoints_line_density=kpoints_line_density,
        )
    except ValueError:
        print("trying higher symprec")
        lobsterin.write_KPOINTS(
            POSCAR_input=fposcar_dst,
            KPOINTS_output=fkpoints_dst,
            line_mode=True,
            symprec=symprec * 2,
            kpoints_line_density=kpoints_line_density,
        )

    # copy our POTCAR from the static calc
    copyfile(fpotcar_src, fpotcar_dst)

    # write a lobsterin file, including fatband analysis
    lobsterin = Lobsterin.standard_calculations_from_vasp_files(
        POSCAR_input=fposcar_dst,
        INCAR_input=fincar_src,
        POTCAR_input=fpotcar_dst,
        option="standard_with_fatband",
    )
    flobsterin = os.path.join(bs_dir, "lobsterin")
    lobsterin.write_lobsterin(flobsterin)

    # write our bs INCAR
    lobsterin.write_INCAR(
        incar_input=fincar_src,
        incar_output=fincar_dst,
        poscar_input=fposcar_dst,
        further_settings={"ISMEAR": 0},
    )

    return bs_dir


def setup_parchg(converged_static_dir, rerun=False, eint=-1):
    """

    function to create input files (INCAR, KPOINTS, POTCAR, POSCAR, WAVECAR, CHGCAR) for partial charge calculation
        after static calculations

    Args:
        converged_static_dir (str)
            path to converged static calculation

        rerun (bool)
            if True, rerun bandstructure calculation even if it's already converged

        eint (flaot)
            the lower energy bound (relative to E_Fermi) to analyze partial charge density

    Returns:
        directory to band structure calculation (str) or None if not ready to run this

    """
    # make sure static is converged
    av = AnalyzeVASP(converged_static_dir)
    if not av.is_converged:
        print("static calculation not converged; not setting up parchg calc yet")
        return None

    # get the paths to relevant input files from the static calculation
    files_from_static = ["POSCAR", "KPOINTS", "POTCAR", "INCAR", "WAVECAR", "CHGCAR"]

    # make a directory for the bandstructure calculation
    parchg_dir = converged_static_dir.replace("-static", "-parchg")
    if not os.path.exists(parchg_dir):
        os.mkdir(parchg_dir)

    # make sure bandstructure calc didn't already run
    av = AnalyzeVASP(parchg_dir)
    if av.is_converged and not rerun:
        print("parchg already converged")
        return None

    new_incar_params = {
        "EINT": str(eint),
        "ISTART": "1",
        "LPARD": "True",
        "LSEPB": "False",
        "LSEPK": "False",
        "LWAVE": "False",
        "NBMOD": "-3",
    }

    for file_to_copy in files_from_static:
        f_src = os.path.join(converged_static_dir, file_to_copy)
        f_dst = os.path.join(parchg_dir, file_to_copy)
        copyfile(f_src, f_dst)

    with open(os.path.join(converged_static_dir, "INCAR")) as f_src:
        with open(os.path.join(parchg_dir, "INCAR"), "w") as f_dst:
            for key in new_incar_params:
                f_dst.write("%s = %s\n" % (key, new_incar_params[key]))
            for line in f_src:
                if line.split("=")[0].strip() in new_incar_params:
                    continue
                f_dst.write(line)

    return parchg_dir


def setup_dfpt(converged_static_dir, supercell_grid=[2, 2, 2], rerun=False):
    """
    function to create input files (INCAR, KPOINTS, POTCAR, POSCAR, WAVECAR, CHGCAR) for partial charge calculation
        after static calculations

    Args:
        converged_static_dir (str)
            path to converged static calculation

        supercell_grid (list)
            the supercell grid to create from original POSCAR

        rerun (bool)
            if True, rerun bandstructure calculation even if it's already converged

    Returns:
        directory to band structure calculation (str) or None if not ready to run this

    """
    # make sure static is converged
    av = AnalyzeVASP(converged_static_dir)
    if not av.is_converged:
        print("static calculation not converged; not setting up dfpt calc yet")
        return None

    # get the paths to relevant input files from the static calculation
    files_from_static = ["POSCAR", "KPOINTS", "POTCAR"]

    # make a directory for the bandstructure calculation
    dfpt_dir = converged_static_dir.replace("-static", "-dfpt")
    if not os.path.exists(dfpt_dir):
        os.mkdir(dfpt_dir)

    # make sure dfpt calc didn't already run
    av = AnalyzeVASP(dfpt_dir)
    if av.is_converged and not rerun:
        print("dfpt already converged")
        return None

    for file_to_copy in files_from_static:
        f_src = os.path.join(converged_static_dir, file_to_copy)
        f_dst = os.path.join(dfpt_dir, file_to_copy)
        copyfile(f_src, f_dst)

    copyfile(
        os.path.join(dfpt_dir, "POSCAR"), os.path.join(dfpt_dir, "POSCAR-unitcell")
    )
    st_unit = StrucTools(os.path.join(dfpt_dir, "POSCAR-unitcell"))
    supercell = st_unit.make_supercell(supercell_grid)
    supercell.to(fmt="POSCAR", filename=os.path.join(dfpt_dir, "POSCAR"))

    fstatic_incar = os.path.join(converged_static_dir, "INCAR")
    fdfpt_incar = os.path.join(dfpt_dir, "INCAR")

    new_incar_params = {
        "IBRION": 7,
        "NSW": 1,
        "IALGO": 38,
        "EDIFF": 1e-6,
        "ADDGRID": True,
        "ALGO": "Normal",
        "ISYM": 2,
    }

    incar_params_to_exclude = ["NPAR", "NCORE"]

    with open(fstatic_incar) as f_src:
        with open(fdfpt_incar, "w") as f_dst:
            for line in f_src:
                if line.split("=")[0].strip() in new_incar_params:
                    continue
                if line.split("=")[0].strip() in incar_params_to_exclude:
                    continue
                if "MAGMOM" in line:
                    magmom = line.split("=")[1].strip()
                    magmoms = magmom.split(" ")
                    new_magmoms = []
                    for mag in magmoms:
                        if mag:
                            old_number = int(mag.split("*")[0])
                            new_number = (
                                old_number
                                * supercell_grid[0]
                                * supercell_grid[1]
                                * supercell_grid[2]
                            )
                            old_mag = mag.split("*")[1]
                            new_mag = old_mag
                            new_magmoms.append("%s*%s" % (new_number, new_mag))
                    f_dst.write("MAGMOM = %s\n" % " ".join(new_magmoms))
                else:
                    f_dst.write(line)
            for key in new_incar_params:
                f_dst.write("%s = %s\n" % (key, new_incar_params[key]))

    fdfpt_kpoints = os.path.join(dfpt_dir, "KPOINTS")
    with open(fdfpt_kpoints, "w") as f_dst:
        f_dst.write("Regular\n")
        f_dst.write("0 0 0\n")
        f_dst.write("Gamma\n")
        f_dst.write("1 1 1\n")

    return dfpt_dir


def generate_finite_displacements(
    converged_static_dir, supercell_grid=[2, 2, 2], remake=False
):
    """
    Args:
        converged_static_dir (str)
            path to converged static calculation

        supercell_grid (list)
            the supercell grid to create from original POSCAR

    Returns:
        phonon_dir
            disp-*/
            POSCAR-*
    """
    # make sure static is converged
    av = AnalyzeVASP(converged_static_dir)
    if not av.is_converged:
        print("static calculation not converged; not setting up phonon calcs yet")
        return None

    # create a directory called phonons within the static directory
    phonon_dir = os.path.join(converged_static_dir, "phonons")
    if not os.path.exists(phonon_dir):
        os.mkdir(phonon_dir)

    # use my current directory as a reference point
    curr_dir = os.getcwd()

    # see if POSCARs are already created
    created_poscars = os.listdir(phonon_dir)
    created_poscars = [f for f in created_poscars if "POSCAR-" in f]

    # go into the phonon directory and generate the displacement POSCARs
    if remake or not created_poscars:
        copyfile(
            os.path.join(converged_static_dir, "CONTCAR"),
            os.path.join(phonon_dir, "POSCAR"),
        )
        os.chdir(phonon_dir)
        subprocess.call(
            [
                "phonopy",
                "-d",
                "--dim=%s %s %s"
                % (
                    str(supercell_grid[0]),
                    str(supercell_grid[1]),
                    str(supercell_grid[2]),
                ),
            ]
        )
        os.chdir(curr_dir)

    # get the paths to relevant input files from the static calculation
    files_from_static = ["KPOINTS", "POTCAR", "INCAR"]

    # some special INCAR settings for the static calculations of each displacement
    new_incar_params = {
        "IBRION": 2,
        "ISIF": 3,
        "ENCUT": 700,
        "EDIFF": 1e-7,
        "LAECHG": False,
        "LREAL": False,
        "ALGO": "Normal",
        "NSW": 0,
        "LCHARG": False,
    }

    # copy KPOINTS, INCAR, POTCAR from the static calculation into phonon_dir
    for file_to_copy in files_from_static:
        f_src = os.path.join(converged_static_dir, file_to_copy)
        f_dst = os.path.join(phonon_dir, file_to_copy)
        copyfile(f_src, f_dst)

    # modify the INCAR in the disp-* dir
    with open(os.path.join(converged_static_dir, "INCAR")) as f_src:
        with open(os.path.join(phonon_dir, "INCAR"), "w") as f_dst:
            for key in new_incar_params:
                f_dst.write("%s = %s\n" % (key, new_incar_params[key]))
            for line in f_src:
                if line.split("=")[0].strip() in new_incar_params:
                    continue
                if "MAGMOM" in line:
                    magmom = line.split("=")[1].strip()
                    magmoms = magmom.split(" ")
                    new_magmoms = []
                    for mag in magmoms:
                        if mag:
                            old_number = int(mag.split("*")[0])
                            new_number = (
                                old_number
                                * supercell_grid[0]
                                * supercell_grid[1]
                                * supercell_grid[2]
                            )
                            old_mag = mag.split("*")[1]
                            new_mag = old_mag
                            new_magmoms.append("%s*%s" % (new_number, new_mag))
                    f_dst.write("MAGMOM = %s\n" % " ".join(new_magmoms))
                    continue
                f_dst.write(line)

    return phonon_dir


def setup_finite_displacement_calcs(phonon_dir, remake=False, rerun=False):

    # grab the created POSCARs
    created_poscars = os.listdir(phonon_dir)
    created_poscars = [f for f in created_poscars if "POSCAR-" in f]

    # get the paths to relevant input files from the static calculation
    files_from_static = ["KPOINTS", "POTCAR", "INCAR"]

    # for each displacement,
    # create a disp-00* directory,
    # grab the POSCAR-00*,
    # copy the static calculation files,
    # modify the INCAR

    statuses = {}

    for poscar in created_poscars:
        number = poscar.split("-")[-1]

        # create disp-00* dir
        disp_dir = os.path.join(phonon_dir, "disp-%s" % number)
        if not os.path.exists(disp_dir):
            os.mkdir(disp_dir)

        statuses[number] = {"convergence": False, "calc_dir": disp_dir}

        # copy the displaced POSCAR-00* into the disp-00* dir
        poscar_src = os.path.join(phonon_dir, poscar)
        poscar_dst = os.path.join(disp_dir, "POSCAR")
        if not os.path.exists(poscar_dst) or remake:
            copyfile(poscar_src, poscar_dst)

        # check convergence
        av = AnalyzeVASP(disp_dir)
        if av.is_converged and not rerun:
            statuses[number]["convergence"] = True
            continue

        # copy KPOINTS, INCAR, POTCAR from the phonon dir into disp_dir
        for file_to_copy in files_from_static:
            f_src = os.path.join(phonon_dir, file_to_copy)
            f_dst = os.path.join(disp_dir, file_to_copy)
            if not os.path.exists(f_dst) or remake:
                copyfile(f_src, f_dst)

    return statuses


def setup_static_magtest(converged_static_dir, rerun=False):
    # make sure relax is converged
    av = AnalyzeVASP(converged_static_dir)
    if not av.is_converged:
        print("static calculation not converged; not setting up static mag test")
        return None

    relax_dir = converged_static_dir.replace("-static", "-relax")
    av_relax = AnalyzeVASP(relax_dir)
    if not av_relax.is_converged:
        print("relax calculation not converged; not setting up static mag test")
        return None

    # get the paths to relevant input files from the static calculation
    files_from_relax = ["POSCAR", "KPOINTS", "POTCAR", "INCAR", "WAVECAR", "CHGCAR"]

    # make a directory for the magtest calculation
    magtest_dir = converged_static_dir.replace("-static", "-static_magtest")
    if not os.path.exists(magtest_dir):
        os.mkdir(magtest_dir)

    # make sure bandstructure calc didn't already run
    av = AnalyzeVASP(magtest_dir)
    if av.is_converged and not rerun:
        print("magtest already converged")
        return None

    mag_decorated_relax_structure = get_structure_from_prev_run(
        av_relax.outputs.vasprun, av_relax.outputs.outcar
    )

    magmom = mag_decorated_relax_structure.site_properties["magmom"]
    magmom_string = " ".join([str(m) for m in magmom])

    new_incar_params = {"MAGMOM": magmom_string}

    for file_to_copy in files_from_relax:
        f_src = os.path.join(converged_static_dir, file_to_copy)
        f_dst = os.path.join(magtest_dir, file_to_copy)
        copyfile(f_src, f_dst)

    with open(os.path.join(converged_static_dir, "INCAR"), "r") as f_src:
        with open(os.path.join(magtest_dir, "INCAR"), "w") as f_dst:
            for key in new_incar_params:
                f_dst.write("%s = %s\n" % (key, new_incar_params[key]))
            for line in f_src:
                if line.split("=")[0].strip() in new_incar_params:
                    continue
                f_dst.write(line)

    return magtest_dir


def main():
    return


if __name__ == "__main__":
    main()
