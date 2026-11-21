Choose CLI tests for every acceptance criterion using the original issue and the evidence associated with each ID. Return scenarios matching the supplied JSON schema.

Every scenario has id, args, markdown, filename, and mode. Use markdown "hello" and begin args with ["-m","hello"]. Add the exact option and value that exercise the criterion. Each argument is a separate string. Do not use -f or reference existing repository files.

Choose one assertion mode per scenario.
- stdout compares the command's exact stdout with the ordinary command for the same Markdown. Set filename to an empty string.
- output_file asserts empty stdout and a named file containing the normal rendered Markdown, using the public renderer as an oracle. Set filename to that output filename.
- preserve_file creates a named file with sentinel contents, executes the command, checks the file remains unchanged, and checks exact normal stdout. Set filename to the file the issue says to leave alone.

Do not write Python or expected HTML. Select modes, option arguments and filenames that test the user's requested behavior. Cover both requested option aliases. The output object has only scenarios.
