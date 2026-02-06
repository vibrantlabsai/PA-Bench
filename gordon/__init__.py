"""
Drop-in replacement for internal gordon TaskVerifier helpers.

Re-exports the dataclasses that scenario verifiers expect.
"""

from pa_bench_sdk.verifier import TaskVerifier

__all__ = ["TaskVerifier"]
