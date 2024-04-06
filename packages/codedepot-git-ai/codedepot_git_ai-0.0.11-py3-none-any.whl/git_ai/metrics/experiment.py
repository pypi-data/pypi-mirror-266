import os
import pygit2
from typing import Optional
import re
import signal
import threading
from git_ai.cmd.ai_repo.ai_repo import AIRepo
from git_ai.errors.errors import ExperimentError
from git_ai.utils import list_path
from git_ai.cmd.constants import AIRepoConstants
from git_ai.metrics.writer import GitTensorboardSummaryWriter


class Experiment(AIRepoConstants):
    _instance = None

    def __new__(cls, *args, **kwargs) -> 'Experiment':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            signal.signal(signal.SIGTERM, cls._instance.close)
            signal.signal(signal.SIGINT, cls._instance.close)
        else:
            raise ExperimentError.experiment_already_started()

        return cls._instance

    def get_new_exp_name(self):
        commit = self.repo.head.target.hex[0:8]
        pattern = re.compile(r'exp/' + commit + '-([0-9]+)')
        this_commit_exps = [
            (b, int(re.match(pattern, b).group(1)))
            for b in self.repo.branches if re.match(pattern, b)
        ]
        latest_commit_id = max(
            this_commit_exps, key=lambda x: x[1], default=(None, -1))[1]
        # Format is exp/commit-id-<latest_commit_id + 1> with the id being a number
        # with 3 digits padded with 0s
        return f"{commit}-{latest_commit_id + 1:03d}"

    def __init__(self, repo_root: Optional[str] = None, **kwargs):
        self.close_lock = threading.Lock()
        self.has_closed = False
        self.repo = AIRepo(path=repo_root)
        if not self.repo.is_ai_initialized():
            raise ExperimentError.repository_not_initialized()

        self.exp_name = self.get_new_exp_name()
        self.original_branch = self.repo.get_current_branch()
        self.writer = GitTensorboardSummaryWriter(repo=self.repo, **kwargs)
        self.start_experiment(self.get_exp_branch() not in self.repo.branches)

    def get_exp_branch(self):
        return "exp/%s" % self.exp_name

    def remove_existing_metrics(self):
        removed_files = (list_path(self.METRICS_PATH) +
                         [self.HPARAMS_JSON_PATH])
        actually_removed = []
        for f in removed_files:
            if os.path.isfile(f):
                os.remove(f)
                actually_removed.append(f)

        # make sure metrics are in git
        actually_removed = [
            f for f in actually_removed if f in self.repo.index]

        return actually_removed

    def commit_dirty_files(self, message, cleanup_message, new, modified, removed):
        self.writer.flush()
        if (new + modified):
            self.repo.commit(new + modified, removed, message)
        elif removed:
            self.repo.commit([], removed, cleanup_message)

    def start_experiment(self, starting_new_experiment):
        try:
            stasher = pygit2.Signature("Git AI", "gitai@gitai.ai")
            if not self.repo.is_empty:
                # Stash dirty files
                new, modified, removed, _ = self.repo.get_wt_modified_files()
                if new or modified or removed:
                    self.repo.stash(stasher, include_untracked=True)
            self.repo.checkout_branch(
                self.get_exp_branch(), new=starting_new_experiment)
            if not self.repo.is_empty:
                # Pop stash and commit dirty files to exp branch
                if new or modified or removed:
                    self.repo.stash_pop(strategy=pygit2.GIT_CHECKOUT_FORCE)
                self.commit_dirty_files(
                    "Experiment cleanup. Committing dirty files", "Experiment cleanup.", new, modified, removed)

                if starting_new_experiment:
                    files = self.remove_existing_metrics()
                    self.repo.commit(
                        [], files, "Removing all metrics to start a new experiment. #EXPERIMENT_ROOT")

            self.repo.make_ai_dirs()
        except Exception as e:
            self.writer.close()
            self.repo.checkout_branch(self.original_branch)
            raise ExperimentError.failed_to_start_experiment() from e

    def push(self):
        self.repo.auth_and_push(
            'origin', f"refs/heads/{self.get_exp_branch()}")

    def checkpoint(self, checkpoint_name: str):
        # TODO Check if current branch is correct
        self.writer.flush()

        self.repo.commit(
            self.metrics_file_list(),
            [],
            "Checkpoint of %s: %s" % (
                self.get_exp_branch(), checkpoint_name
            ),
        )

        # Check if there a remote to push to
        if 'origin' not in [r.name for r in self.repo.remotes]:
            return
        else:
            self.push()

    def end_experiment(self):
        self.writer.close()
        to_add, to_remove = self.repo.get_ai_modified_files()
        if to_add or to_remove:
            self.repo.commit(to_add, to_remove, "End of experiment commit")
        try:
            if [r for r in self.repo.remotes if r.name == 'origin']:
                self.push()
        except Exception as e:
            print("Warning: Failed to push experiment branch. %s" % e)
        self.repo.checkout_branch(self.original_branch)

    def __enter__(self):
        # Checks if experiment branch exists
        return self

    def close(self, signum=None, frame=None):
        with self.close_lock:
            if self.has_closed:
                return
            self.has_closed = True
            self.end_experiment()
            Experiment._instance = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
