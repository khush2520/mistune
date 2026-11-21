Write a complete, small pytest file for the candidate's acceptance criteria. The runner writes it to tests/test_autose_issue.py. Supply all required imports. Use public entry points and deterministic inputs. Use the acceptance criterion IDs as function names: AC-01 uses test_ac_01 or test_ac_01_description. Test each criterion. Keep tests independent. Verify expected output with an assertion. If this is a retry, replace the whole previous generated test module and fix the actual failure.

For CLI subprocess tests, derive the repository src path as Path(__file__).resolve().parents[1] / "src" and pass that absolute path via PYTHONPATH. Alternatively invoke cli with sys.argv and capsys or a StringIO stub.

Return only JSON with test_code as one string containing the complete Python test module. Do not emit a file path, a diff, commentary or a Markdown fence.
