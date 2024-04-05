import os
import re
import shutil
import sys
import tempfile
import logging
import itertools as it
from binascii import b2a_hex
from datetime import datetime
from io import BytesIO
from six.moves.configparser import ConfigParser
from shutil import rmtree
from collections import defaultdict
from contextlib import contextmanager
import codecs

os.environ['HGRCPATH'] = ''  # disable loading .hgrc
# ensure commit messages etc get decoded, otherwise falls back to envvars like LANG/LC_ALL which might be ascii/C
os.environ['HGENCODING'] = 'UTF-8'
import mercurial
from mercurial import ui, hg, cmdutil, commands, scmutil, copies, logcmdutil
from mercurial.error import RepoLookupError, RevlogError

import tg
from paste.deploy.converters import asbool
from pymongo.errors import DuplicateKeyError
from tg import tmpl_context as c
import six
from ming.base import Object
from ming.odm import Mapper, state, session
from ming.odm.base import ObjectState
from ming.utils import LazyProperty

from allura import model as M
from allura.lib import helpers as h
from allura.model.repository import (
    topological_sort,
    GitLikeTree,
    zipdir,
    Commit,
    CommitDoc,
    Tree,
)

log = logging.getLogger(__name__)

prepare_noop = lambda ctx, fns: None


class Repository(M.Repository):
    tool_name='Hg'
    repo_id='hg'
    type_s='Hg Repository'
    class __mongometa__:
        name = 'hg-repository'

    @LazyProperty
    def _impl(self):
        return HgImplementation(self)

    def merge_command(self, merge_request):
        '''Return the command to merge a given commit into a given target branch'''
        cmd = 'hg checkout {}\nhg pull -r {} {}'.format(
            merge_request.target_branch,
            merge_request.downstream.commit_id,
            merge_request.downstream_repo.clone_url_first(anon=False, username=c.user.username),
        )
        cmd += '\nhg merge -r {}\nhg commit -m "Merge {}"'.format(
            merge_request.downstream.commit_id,
            merge_request.source_branch,
        )
        return cmd

    @contextmanager
    def _tmp_clone(self, hgui_stdout=False):
        tmp_path = tempfile.mkdtemp()
        # !$ hg doesn't like unicode as urls
        _, tmp_repo = hg.clone(
            HgUI(stdout=hgui_stdout),
            {},
            self.full_fs_path.encode('utf-8'),
            tmp_path.encode('utf-8'),
            update=False)
        try:
            yield tmp_repo.local()
        finally:
            shutil.rmtree(tmp_path, ignore_errors=True)

    def _merge(self, mr, tmp_repo, _ui):
        """Common code for :meth can_merge: and :meth merge:

        Returns a tuple (has_conflicts_flag, exception_or_none).
        """
        # switch to target branch and update working copy to it
        target_branch_b = mr.target_branch.encode('utf-8')
        source_branch_b = mr.source_branch.encode('utf-8')
        if target_branch_b not in tmp_repo.branchmap():
            commands.branch(_ui, tmp_repo, target_branch_b)
        commands.update(_ui, tmp_repo, target_branch_b)
        # pull source branch
        commands.pull(
            _ui,
            tmp_repo,
            mr.downstream_repo.full_fs_path.encode('utf-8'),
            branch=[source_branch_b])

        try:
            res = commands.merge(_ui, tmp_repo, source_branch_b)
            # merge can return 0 or False if there are no conflicts
            conflicts = bool(res)
        except hg.error.Abort as e:
            if str(e) == 'nothing to merge':
                conflicts = False
            else:
                log.info('hg merge error', exc_info=True)
                return True, e
        return conflicts, None

    def can_merge(self, mr, stdout=False):
        """
        Given merge request `mr` determine if it can be merged w/o conflicts.
        """
        with self._tmp_clone(hgui_stdout=stdout) as tmp_repo:
            has_conflicts, _ = self._merge(mr, tmp_repo, HgUI(stdout=stdout))
            return not has_conflicts

    def merge(self, mr):
        with self._tmp_clone() as tmp_repo:
            _ui = HgUI()
            has_conflicts, exc = self._merge(mr, tmp_repo, _ui)
            if not has_conflicts:
                msg = 'Merge {} branch {} into {}\n\n{}'.format(
                    mr.downstream_repo.url(),
                    mr.source_branch,
                    mr.target_branch,
                    h.absurl(mr.url()))
                author = h.really_unicode(
                    c.user.display_name or c.user.username)
                commands.commit(_ui, tmp_repo, message=six.ensure_binary(msg), user=six.ensure_binary(author))
                commands.push(
                    _ui,
                    tmp_repo,
                    six.ensure_binary(self.full_fs_path),
                    new_branch=True,
                    branch=[six.ensure_binary(mr.target_branch)])
            else:
                exc = exc or Exception("Can't merge %s" % mr.url())
                raise exc

    def rev_to_commit_id(self, rev):
        return self._impl.rev_parse(rev)

    def get_tags(self, for_merge_request=False):
        """
        Override:
            must remove 'tip' from choices for merge request since Mercurial doesn't allow it as a merge source or dest
            and our current implementation doesn't work for any other tag names either (maybe could in the future?)
        """
        if not for_merge_request:
            return super().get_tags()
        else:
            return []


class HgUI(ui.ui):
    '''Hg UI subclass that suppresses reporting of untrusted hgrc files.'''
    def __init__(self, *args, **kwargs):
        stdout = kwargs.pop('stdout', False)
        super().__init__(*args, **kwargs)
        self.setconfig(b'ui', b'report_untrusted', b'off', b'allura')
        self.setconfig(b'progress', b'disable', b'true', b'allura')
        self.setconfig(b'ui', b'nontty', b'true', b'allura')
        if stdout:
            # for easier debugging (in tests).  Probably not relevant with pytest?
            if six.PY3 and hasattr(sys.stdout, 'buffer'):
                self.fout = sys.stdout.buffer
            else:
                self.fout = sys.stdout
            # self.ferr = sys.stdout  # doesn't work and makes error output disappear completely


class HgImplementation(M.RepositoryImplementation):
    re_hg_user = re.compile(b'(.*) <(.*)>')

    def __init__(self, repo):
        self._repo = repo

    @LazyProperty
    def _hg(self):
        try:
            return hg.repository(HgUI(), six.ensure_binary(self._repo.full_fs_path))
        except hg.error.RepoError as e:
            log.error('Error looking up repo at %s: %s',
                    self._repo.full_fs_path, e)
            return None

    def revtype(self, commit_id):
        # helper to look up a commit if it is a symbolic name, and convert from unicode to str
        # as of hg 4.7, hgrepo __getattr__ , which calls changectx(), limited its support to exact rev identifiers
        # so we must do extra work now to locate a rev
        # Recommendations from: https://www.mercurial-scm.org/repo/hg/file/4.6/mercurial/context.py#l380

        if commit_id is None:
            return None
        elif isinstance(commit_id, int):
            return commit_id

        commit_id = six.ensure_binary(commit_id)

        if len(commit_id) not in (20, 40):
            return scmutil.revsymbol(self._hg, commit_id)

        return commit_id

    def branchtags(self):
        '''Return a dict where branch names map to the tipmost head of
        the branch, open heads only

        It's re-implementation of hg API method, which was removed in latest versions.
        '''
        bt = {}
        for bn, heads in self._hg.branchmap().items():
            head = None
            for i in range(len(heads)-1, -1, -1):
                _head = heads[i]
                if b'close' not in self._hg.changelog.read(_head)[5]:
                    head = _head
                    break
            # an open head was found (branch is not closed)
            if head is not None:
                bt[bn] = head
        return bt

    def init(self):
        fullname = self._setup_paths()
        log.info('hg init %s', fullname)
        if os.path.exists(fullname):
            shutil.rmtree(fullname)
        repo = hg.repository(HgUI(), six.ensure_binary(self._repo.full_fs_path), create=True)
        self.__dict__['_hg'] = repo
        self._setup_special_files()
        self._repo.set_status('ready')

    def clone_from(self, source_url):
        '''Initialize a repo as a clone of another'''
        self._repo.set_status('cloning')
        log.info('Initialize %r as a clone of %s',
                 self._repo, source_url)
        try:
            fullname = self._setup_paths(create_repo_dir=False)
            if os.path.exists(fullname):
                shutil.rmtree(fullname)
            # !$ hg doesn't like unicode as urls
            srcpeer, destpeer = hg.clone(
                HgUI(),
                {},
                source_url.encode('utf-8'),
                self._repo.full_fs_path.encode('utf-8'),
                update=False)
            self.__dict__['_hg'] = destpeer.local()
            self._setup_special_files(source_url)
        except Exception:
            self._repo.set_status('ready')
            raise

    def commit(self, rev):
        '''Return a Commit object.  rev can be _id or a branch/tag name'''
        if not self._hg:
            return None
        result = Commit.query.get(_id=rev)
        if result is None:
            try:
                impl = self._hg[self.revtype(rev)]
                result = Commit.query.get(_id=impl.hex().decode('utf-8'))
            except RepoLookupError as e:
                # we expect lots of "unknown revision 'default'" etc if a branch doesn't exist
                log.info("Didn't find commit: %s", rev, exc_info=e)
        if result is None:
            return None
        result.set_context(self._repo)
        return result

    def real_parents(self, ci):
        """Return all parents of a commit, excluding the 'null revision' (a
        fake revision added as the parent of the root commit by the Hg api).
        """
        return [p for p in ci.parents() if p]

    def all_commit_ids(self):
        """Return a list of commit ids, starting with the head(s) and ending
        with the root (first commit) of the tree.
        """
        graph = {}
        to_visit = [ self._hg[hd] for hd in self._hg.heads() ]
        while to_visit:
            obj = to_visit.pop()
            if obj.hex() in graph: continue
            parents = self.real_parents(obj)
            graph[obj.hex()] = {
                p.hex() for p in parents
                if p.hex() != obj.hex()}
            to_visit += parents
        return reversed([ci.decode('utf-8') for ci in topological_sort(graph)])

    def new_commits(self, all_commits=False):
        graph = {}
        to_visit = [ self._hg[hd] for hd in self._hg.heads() ]
        while to_visit:
            obj = to_visit.pop()
            if obj.hex() in graph: continue
            if not all_commits:
                # Look up the object
                if Commit.query.find(dict(_id=obj.hex().decode('utf-8'))).count():
                    graph[obj.hex()] = set() # mark as parentless
                    continue
            parents = self.real_parents(obj)
            graph[obj.hex()] = {
                p.hex() for p in parents
                if p.hex() != obj.hex()}
            to_visit += parents
        return [ci.decode('utf-8') for ci in topological_sort(graph)]

    def refresh_commit_info(self, oid, seen, lazy=True):
        oid = six.ensure_str(oid)
        ci_doc = CommitDoc.m.get(_id=oid)
        if ci_doc and lazy: return False
        obj = self._hg[self.revtype(oid)]
        # Save commit metadata
        mo = self.re_hg_user.match(obj.user())
        if mo:
            user_name, user_email = mo.groups()
        else:
            user_name = user_email = obj.user()
        user = Object(
            name=h.really_unicode(user_name),
            email=h.really_unicode(user_email),
            date=datetime.utcfromtimestamp(obj.date()[0]))
        fake_tree = self._tree_from_changectx(obj)
        args = dict(
            tree_id=fake_tree.hex(),
            committed=user,
            authored=user,
            message=h.really_unicode(obj.description() or ''),
            child_ids=[],
            parent_ids=[p.hex().decode('utf-8') for p in self.real_parents(obj)
                        if p.hex().decode('utf-8') != obj.hex().decode('utf-8')])
        if ci_doc:
            ci_doc.update(args)
            ci_doc.m.save()
        else:
            ci_doc = CommitDoc(dict(args, _id=oid))
            try:
                ci_doc.m.insert()
            except DuplicateKeyError:
                if lazy: return False
        self.refresh_tree_info(fake_tree, seen, lazy)
        return True

    def refresh_tree_info(self, tree, seen, lazy=True):
        tree_hex = six.ensure_text(tree.hex())
        if lazy and tree_hex in seen: return
        seen.add(tree_hex)
        doc = Tree(
            _id=tree_hex,
            tree_ids=[],
            blob_ids=[],
            other_ids=[])
        for name, t in tree.trees.items():
            self.refresh_tree_info(t, seen, lazy)
            doc.tree_ids.append(
                dict(name=h.really_unicode(name), id=six.ensure_text(t.hex())))
        for name, oid in tree.blobs.items():
            doc.blob_ids.append(
                dict(name=h.really_unicode(name), id=oid))
        # set to 'dirty' to force save() to be used instead of insert() (which errors if doc exists in db already)
        state(doc).status = ObjectState.dirty
        session(doc).flush(doc)
        session(doc).expunge(doc)
        return doc

    def _commit_info(self, ctx):
        """Returns dict with info about commit

        :param ctx: hg's change context
        """
        branches = defaultdict(list)
        for name, head in self.branchtags().items():
            branches[self._hg[head].hex().decode('utf-8')].append(name)
        user = ctx.user()
        match = self.re_hg_user.match(user)
        if match:
            name, email = match.groups()
        else:
            name, email = (user or '--none--', '')
        return {
            'id': ctx.hex().decode('utf-8'),
            'message': h.really_unicode(ctx.description() or '--none--'),
            'authored': {
                    'name': h.really_unicode(name),
                    'email': h.really_unicode(email),
                    'date': datetime.utcfromtimestamp(ctx.date()[0]),
                },
            'committed': {
                    'name': h.really_unicode(name),
                    'email': h.really_unicode(email),
                    'date': datetime.utcfromtimestamp(ctx.date()[0]),
                },
            'refs': [r.decode('utf-8') for r in branches[ctx.hex().decode('utf-8')] + ctx.tags()],
            'parents': [pctx.hex().decode('utf-8') for pctx in ctx.parents() if pctx.rev() > -1],
            'size': None,
            'rename_details': {},
        }

    def log(self, revs=None, path=None, exclude=None, id_only=True, **kw):
        path = path.strip('/').encode('utf-8') if path else None
        revs = [six.ensure_binary('%s:0' % r) for r in revs or []]
        pats = [b'path:%s' % path] if path else []
        exclude = exclude or []  # don't think a `exclude` value is ever passed to this function, could drop it?
        walkerrevs, makefilematcher = logcmdutil.makewalker(self._hg, logcmdutil.walkopts(
            pats=pats,
            opts={},
            revspec=revs,
            exclude_pats=exclude,
            force_changelog_traversal=True,  # required for removed/renamed files to be found
        ))
        change_revs = scmutil.walkchangerevs(self._hg, walkerrevs, makefilematcher, prepare_noop)
        for ctx in change_revs:
            if id_only:
                yield ctx.hex().decode('utf-8')
            else:
                rename_details = {}
                if path and path in ctx.files() and ctx[path].renamed():
                    rename_details['path'] = '/' + six.ensure_str(ctx[path].renamed()[0])
                    rename_details['commit_url'] = self._repo.url_for_commit(
                        ctx.hex().decode('utf-8')
                    )
                commit = self._commit_info(ctx)
                commit.update({
                    'size': int(ctx[path].size()) if path in ctx else None,
                    'rename_details': rename_details,
                })
                yield commit
                if rename_details:
                    # we do not need to show commits before rename
                    break

    def open_blob(self, blob):
        fctx = self._hg[self.revtype(blob.commit._id)][h.really_unicode(blob.path()).encode('utf-8')[1:]]
        return BytesIO(fctx.data())

    def blob_size(self, blob):
        fctx = self._hg[self.revtype(blob.commit._id)][h.really_unicode(blob.path()).encode('utf-8')[1:]]
        return fctx.size()

    def _setup_hooks(self, source_path=None):
        'Set up the hg changegroup hook'
        hgrc = os.path.join(self._repo.fs_path, self._repo.name, '.hg', 'hgrc')
        cp = ConfigParser()
        cp.read(hgrc)
        if not cp.has_section('hooks'):
            cp.add_section('hooks')
        url = self._repo.refresh_url()
        cp.set('hooks','; = [the next line is required for site integration, do not remove/modify]', '')
        cp.set('hooks','changegroup.sourceforge','curl -s %s' % url)
        with codecs.open(hgrc, 'w') as fp:
            cp.write(fp)
        os.chmod(hgrc, 0o755)

    def _tree_from_changectx(self, changectx):
        '''Build a fake git-like tree from a changectx and its manifest'''
        root = GitLikeTree()
        for filepath in changectx.manifest():
            fctx = changectx[filepath]
            oid = six.ensure_str(b2a_hex(fctx.filenode()))
            root.set_blob(filepath, oid)
        return root

    def symbolics_for_commit(self, commit):
        try:
            ctx = self._hg[self.revtype(commit._id)]
        except RepoLookupError as e:
            return [], []
        return [h.really_unicode(ctx.branch())], list(map(h.really_unicode, ctx.tags()))

    def rev_parse(self, rev):
        try:
            return self._hg[self.revtype(rev)].hex().decode('utf-8')
        except RepoLookupError as e:
            return None

    def compute_tree_new(self, commit, tree_path='/'):
        ctx = self._hg[self.revtype(commit._id)]
        fake_tree = self._tree_from_changectx(ctx)
        fake_tree = fake_tree.get_tree(tree_path)
        tree = self.refresh_tree_info(fake_tree, set())
        return tree._id

    def tarball(self, commit, path=None):
        """
        :param path: is currently ignored.  Can't request a snapshot of a subdirectory

        Makes a hg archive at `tmpdest`
            then zips that into `dest/tmpfilename`
            then renames that to `dest/filename`

        Could try modifying commands.archive(...) call to pass type='zip' and avoid temp files, although it would use
        python's zipfile implementation.  And also would need to set HgUI's setting for ui.archivemeta to False,
        to omit .hg_archival.txt
        """
        if not os.path.exists(self._repo.tarball_path):
            os.makedirs(self._repo.tarball_path)
        if not os.path.exists(self._repo.tarball_tmpdir):
            os.makedirs(self._repo.tarball_tmpdir)
        archive_name = self._repo.tarball_filename(commit)
        dest = os.path.join(self._repo.tarball_path, archive_name)
        tmpdest = os.path.join(self._repo.tarball_tmpdir, archive_name)
        filename = os.path.join(self._repo.tarball_path, '{}{}'.format(archive_name, '.zip'))
        tmpfilename = os.path.join(self._repo.tarball_path, '{}{}'.format(archive_name, '.tmp'))
        # We need to convert dest to str here, since commands.archive and
        # shutil.* don't play nicely with unicode on py2. See [#7757] for details
        dest = six.ensure_str(h.really_unicode(dest))
        rmtree(dest, ignore_errors=True)
        tmpdest = six.ensure_str(tmpdest)
        rmtree(tmpdest, ignore_errors=True)
        try:
            # no self.revtype() usage here, since archive() calls revsingle() on the commit id
            commands.archive(HgUI(), self._hg, six.ensure_binary(tmpdest), rev=commit.encode('utf-8'), prefix=b'')
            basedir = os.path.basename(tmpdest)
            zipdir(tmpdest, tmpfilename, exclude=basedir + '/.hg_archival.txt')
            os.rename(tmpfilename, filename)
        finally:
            rmtree(dest, ignore_errors=True)
            rmtree(tmpdest, ignore_errors=True)
            if os.path.exists(tmpfilename):
                os.remove(tmpfilename)

    def is_empty(self):
        return not self._hg or self._hg.heads() == [b'\x00'*20]

    def is_file(self, path, rev=None):
        return six.ensure_binary(path.strip('/')) in self._hg[self.revtype(rev)]

    @LazyProperty
    def head(self):
        return self._hg[self._hg.tags()[b'tip']].hex().decode('utf-8')

    @LazyProperty
    def heads(self):
        return [Object(name=None, object_id=self._hg[v].hex().decode('utf-8')) for v in self._hg.heads()]

    @LazyProperty
    def branches(self):
        return [Object(name=h.really_unicode(branch), object_id=self._hg[head].hex().decode('utf-8'))
                for branch, head in self.branchtags().items()]

    @LazyProperty
    def tags(self):
        return [Object(name=h.really_unicode(k), object_id=self._hg[v].hex().decode('utf-8'))
                for k, v in self._hg.tags().items()]

    def set_default_branch(self, name):
        if not name:
            return
        self._repo.default_branch_name = name

    def _get_last_commit(self, commit_id, paths):
        walkerrevs, makefilematcher = logcmdutil.makewalker(self._hg, logcmdutil.walkopts(
            pats=[six.ensure_binary('path:%s' % p) for p in paths],
            opts={},
            revspec=[six.ensure_binary('%s:0' % commit_id)],
            force_changelog_traversal=True,  # required for removed/renamed files to be found
        ))

        # walkchangerevs appears to occasionally, randomly throw either a
        # RevlogError or an mpatch.mpatchError complaining about corrupt
        # repo data.  However, it's not reproducable and even just retrying
        # the call once immediately is enough to clear the error.
        # http://stackoverflow.com/questions/17073368/mercurial-complains-repository-is-corrupt-when-its-not
        # seems to indicate it may be related to optimizations in the network
        # stack, but I wasn't able to apply that solution, so this retry loop
        # is a work-around.
        for attempt in range(1, 3):
            try:
                ctx = next(iter(scmutil.walkchangerevs(self._hg, walkerrevs, makefilematcher, prepare_noop)))
            except StopIteration:
                return None, set()
            except Exception as e:
                # only catch these two types; unfortunately, can't seem to
                # import mpatchError because it's raised in an .so library
                if not (isinstance(e, RevlogError) or type(e).__name__ == 'mpatchError'):
                    raise
                if attempt == 2:
                    log.exception('Error in mercurial repo: %s on %s in %s', e, commit_id, self._repo.full_fs_path)
                    return None, set()
                else:
                    log.error('Potentially spurious error (retrying): %s on %s in %s', e, commit_id, self._repo.full_fs_path)
            else:
                return ctx.hex().decode('utf-8'), {h.really_unicode(f) for f in ctx.files()}

    def get_changes(self, commit_id):
        return self._hg[self.revtype(commit_id)].files()

    def paged_diffs(self, commit_id, start=0, end=None, onlyChangedFiles=False):
        result = {'added': [], 'removed': [], 'changed': [], 'copied': [], 'renamed': [], 'total': 0}
        # equivalent to `hg status --change <commit_id>`, but using hg API
        node2 = self._hg[self.revtype(commit_id)].node()
        node1 = self._hg[node2].p1().node()

        status = self._hg.status(node1, node2)

        if asbool(tg.config.get('scm.commit.hg.detect_copies', False)):
            _copies = copies.pathcopies(self._hg[node1], self._hg[node2])
            for k, v in _copies.items():
                result['copied'].append({
                    'new': h.really_unicode(k),
                    'old': h.really_unicode(v),
                    'ratio': 1,
                })

        # reformat status to apply pagination
        files = []
        for name in status.modified:
            s = ('M', h.really_unicode(name))
            files.append(s)
        for name in status.added:
            s = ('A', h.really_unicode(name))
            files.append(s)
        for name in status.removed:
            s = ('R', h.really_unicode(name))
            files.append(s)
        result['total'] = len(files)
        for s, name in files[start:end]:
            if s == 'A':
                result['added'].append(name)
            elif s == 'M':
                result['changed'].append(name)
            elif s == 'R':
                result['removed'].append(name)

        for r in result['copied'][:]:
            if r['old'] in result['removed']:
                result['removed'].remove(r['old'])
                result['copied'].remove(r)
                result['renamed'].append(r)
            try:
                result['added'].remove(r['new'])
            except ValueError:
                # Was already removed probably because it was copied with the 'hg copy' command.
                pass

        return result

    def _outgoing(self, ui, repo, dest, opts):
        """This is inspired heavily by hg.outgoing function (from 3.0)

        The changes are:
            - yields the list of commits, instead of printing them to stdout
            - does not handle subrepos
            - uses default options for "force" and "bundle" if not provided
            - does not trigger hooks
            - newest_first = True by default
        """
        if b'force' not in opts:
            opts[b'force'] = False
        if b'bundle' not in opts:
            opts[b'bundle'] = None
        if b'newest_first' not in opts:
            opts[b'newest_first'] = True
        limit = hg.logcmdutil.getlimit(opts)
        o, other = hg._outgoing(ui, repo, [six.ensure_binary(dest)], opts)
        if not o:
            return

        if opts.get(b'newest_first'):
            o.reverse()
        commits = []
        count = 0
        for n in o:
            if limit is not None and count >= limit:
                break
            parents = [p for p in repo.changelog.parents(n) if p != mercurial.node.nullid]
            if opts.get(b'no_merges') and len(parents) == 2:
                continue
            count += 1
            yield repo[n]

    def merge_request_commits(self, mr):
        """
        Return list of commits to be merged

        Must be called within mr.push_downstream_context()
        """
        dest = mr.app.repo.full_fs_path
        opts = {b'branch': [six.ensure_binary(mr.source_branch)],
                b'rev': [self.revtype(mr.downstream.commit_id)]}
        commits = self._outgoing(HgUI(), self._hg, dest, opts)
        # don't show children of downstream commit id
        not_top = lambda ci: ci.hex().decode('utf-8') != mr.downstream.commit_id
        commits = it.dropwhile(not_top, commits)
        return list(map(self._commit_info, commits))


Mapper.compile_all()
