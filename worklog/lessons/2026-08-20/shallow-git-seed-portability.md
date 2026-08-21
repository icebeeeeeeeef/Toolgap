# Shallow Git seed portability

Canonical owner: `docs/DECISIONS.md` D025.

A shallow repository can produce a bundle that passes `git bundle verify` yet
cannot be cloned because the shallow parent boundary is not represented as a
self-contained bundle prerequisite. Test the consuming operation, not only the
container verifier.

For this attempt, a portable archive of the shallow bare repository retained
the boundary and cloned correctly. macOS tar initially carried Apple xattrs and
the local UID, which Ubuntu rejected as dubious ownership. Removing xattrs and
normalizing archive ownership to uid/gid 0 produced the accepted cross-host
seed. The frozen archive is still only transport; commit/tree remain the source
identity.
